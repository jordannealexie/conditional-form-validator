from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User, RefreshToken
from app.schemas.auth import Token, UserCreate, UserResponse, TokenData, RefreshRequest
from app.core.security import create_access_token, create_refresh_token, verify_password, get_password_hash
from sqlalchemy import select
from app.utils.rate_limit import rate_limiter
from app.dependencies.audit import get_audit_service
from app.services.audit import AuditService
from app.db.session import get_db
from app.core.config import settings
from app.dependencies.auth import get_current_user, get_current_active_user

router = APIRouter()

@router.post("/register", response_model=UserResponse)
async def register(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    audit: AuditService = Depends(get_audit_service)
):
    """Register a new user"""
    # Check if user exists
    result = await db.execute(
        select(User).where(User.email == user_in.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        await audit.log("register", status="failure", details=f"Email already exists: {user_in.email}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Compute full_name if not provided
    full_name = user_in.full_name
    if not full_name and (user_in.first_name or user_in.last_name):
        full_name = f"{user_in.first_name or ''} {user_in.last_name or ''}".strip()
    
    # Create new user
    user = User(
        email=user_in.email,
        username=user_in.username,
        password_hash=get_password_hash(user_in.password),
        user_role=user_in.user_role,
        bank_id=user_in.bank_id,
        first_name=user_in.first_name,
        last_name=user_in.last_name,
        full_name=full_name,
        department=user_in.department,
        level=user_in.level,
        location=user_in.location,
        updated_at=datetime.now(timezone.utc)
    )
    
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    await audit.log("register", user_id=user.id, username=user.username, details={"msg": f"New user registered: {user.username}"})
    
    return user


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
    audit: AuditService = Depends(get_audit_service)
):
    """Login and get access token"""
    # 1. Rate Limiting
    client_ip = request.client.host if request.client else "unknown"
    await rate_limiter.check(f"login:{client_ip}", limit=5, window_seconds=60)
    
    # Try username first, then email
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    print(f"DEBUG: After username lookup, user: {user is not None}, id: {user.id if user else None}")

    # If username not found, try email
    if not user:
        result = await db.execute(
            select(User).where(User.email == form_data.username)
        )
        user = result.scalar_one_or_none()
        print(f"DEBUG: After email lookup, user: {user is not None}, id: {user.id if user else None}")

    if not user or not verify_password(form_data.password, user.password_hash):
        print(f"DEBUG: Login failed for user {form_data.username}, entered password: {form_data.password}")
        print(f"DEBUG: User found: {user is not None}, hash: {user.password_hash if user else None}")
        await audit.log("login_attempt", user_id=user.id if user else None, status="failure", details="Incorrect credentials")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.active:
        await audit.log("login_attempt", user_id=user.id, status="failure", details="Inactive account")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    # Sync user roles to Casbin on login to ensure fresh permissions
    from app.core.casbin_enforcer import casbin_enforcer
    from sqlalchemy.orm import selectinload
    
    try:
        # Reload user with roles relationship
        result = await db.execute(
            select(User).options(selectinload(User.roles)).where(User.id == user.id)
        )
        user = result.scalar_one_or_none()
        
        # Sync user roles to Casbin
        if user and user.user_role:
            role_names = [user.user_role]
            print(f"DEBUG: Syncing roles for user {user.username}: {role_names}")
            casbin_enforcer.sync_user_roles(user.username, role_names)
    except Exception as e:
        print(f"Warning: Could not sync roles to Casbin: {e}")
    
    # Get user permissions from Casbin (through roles)
    permissions = []
    try:
        # Get direct permissions for user
        policy = casbin_enforcer.get_permissions_for_user(user.username)
        permissions = [f"{p[1]}:{p[2]}" for p in policy if len(p) >= 3]
        
        # Also get implicit permissions through roles
        roles = casbin_enforcer.get_roles_for_user(user.username)
        print(f"DEBUG: User {user.username} has roles in Casbin: {roles}")
        for role in roles:
            role_perms = casbin_enforcer.get_permissions_for_role(role)
            print(f"DEBUG: Role {role} has permissions: {role_perms}")
            for p in role_perms:
                if len(p) >= 3:
                    perm_str = f"{p[1]}:{p[2]}"
                    if perm_str not in permissions:
                        permissions.append(perm_str)
    except Exception as e:
        print(f"Warning: Could not get permissions from Casbin: {e}")
    
    # Token payload: user_id, username, user_role, bank_id, permissions
    token_data = {
        "user_id": user.id,
        "sub": user.username,
        "user_role": user.user_role,
        "bank_id": user.bank_id,
        "permissions": permissions
    }
    
    access_token = create_access_token(data=token_data)
    refresh_token_jwt = create_refresh_token(data={"sub": user.username})
    
    # Store refresh token in DB
    from app.core.config import settings
    db_refresh_token = RefreshToken(
        user_id=user.id,
        token=refresh_token_jwt,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    )
    db.add(db_refresh_token)
    await db.commit()
    
    await audit.log("login", user_id=user.id, username=user.username, details="Login success")
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token_jwt,
        "token_type": "bearer"
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using a valid refresh token. Body: { \"refresh_token\": \"...\" }"""
    from jose import jwt, JWTError
    refresh_token_in = body.refresh_token
    try:
        payload = jwt.decode(refresh_token_in, settings.SECRET_KEY, algorithms=["HS256"])
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        username = payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Check if token exists and is not revoked
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == refresh_token_in,
            RefreshToken.revoked == False,
            RefreshToken.expires_at > datetime.utcnow()
        )
    )
    db_token = result.scalar_one_or_none()
    if not db_token:
        raise HTTPException(status_code=401, detail="Refresh token revoked or expired")
    
    # Get user
    result = await db.execute(select(User).where(User.id == db_token.user_id))
    user = result.scalar_one_or_none()
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    
    # Generate new tokens
    # Get user permissions (simplified)
    from app.core.casbin_enforcer import casbin_enforcer
    permissions = []
    try:
        policy = casbin_enforcer.get_permissions_for_user(user.username)
        permissions = [f"{p[1]}:{p[2]}" for p in policy]
    except Exception: pass
    
    token_data = {
        "user_id": user.id,
        "sub": user.username,
        "user_role": user.user_role,
        "bank_id": user.bank_id,
        "permissions": permissions
    }
    
    new_access_token = create_access_token(data=token_data)
    
    return {
        "access_token": new_access_token,
        "refresh_token": refresh_token_in, # Reuse same refresh token or rotate? Reuse for now.
        "token_type": "bearer"
    }


@router.post("/logout")
async def logout(
    refresh_token_in: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Logout and revoke refresh token"""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == refresh_token_in)
    )
    db_token = result.scalar_one_or_none()
    if db_token:
        db_token.revoked = True
        await db.commit()
    
    return {"msg": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_active_user)):
    """Get current user profile"""
    return current_user