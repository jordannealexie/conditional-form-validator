--
-- PostgreSQL database dump
--

\restrict Te6H1lx00Sx1xnPxBEKxNVYKBvkmxeCEucGWhcvxpG1CbFdHUxKAM1ibnxdw5io

-- Dumped from database version 15.15
-- Dumped by pg_dump version 16.11 (Ubuntu 16.11-0ubuntu0.24.04.1)

-- Started on 2026-02-04 08:18:09 UTC

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- TOC entry 5 (class 2615 OID 26842)
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it


ALTER SCHEMA public OWNER TO postgres;

--
-- TOC entry 3685 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS '';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 219 (class 1259 OID 26866)
-- Name: abac_policies; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.abac_policies (
    id integer NOT NULL,
    name character varying NOT NULL,
    description character varying,
    rules json NOT NULL,
    is_active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.abac_policies OWNER TO postgres;

--
-- TOC entry 218 (class 1259 OID 26865)
-- Name: abac_policies_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.abac_policies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.abac_policies_id_seq OWNER TO postgres;

--
-- TOC entry 3687 (class 0 OID 0)
-- Dependencies: 218
-- Name: abac_policies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.abac_policies_id_seq OWNED BY public.abac_policies.id;


--
-- TOC entry 245 (class 1259 OID 27101)
-- Name: audit_logs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.audit_logs (
    id integer NOT NULL,
    user_id integer,
    username character varying,
    action character varying NOT NULL,
    resource_type character varying,
    resource_id character varying,
    status character varying,
    ip_address character varying,
    user_agent character varying,
    payload json,
    details json,
    changes json,
    created_by integer,
    updated_by integer,
    deleted_by integer,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    page character varying(100),
    entity_name character varying(100),
    entity_id character varying(100),
    changed_fields jsonb
);


ALTER TABLE public.audit_logs OWNER TO postgres;

--
-- TOC entry 3688 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN audit_logs.changes; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.changes IS 'Before and after values in JSON format';


--
-- TOC entry 3689 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN audit_logs.created_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.created_by IS 'User ID who created this record';


--
-- TOC entry 3690 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN audit_logs.updated_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.updated_by IS 'User ID who updated this record';


--
-- TOC entry 3691 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN audit_logs.deleted_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.deleted_by IS 'User ID who deleted this record';


--
-- TOC entry 3692 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN audit_logs.page; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.page IS 'Page/module where action occurred';


--
-- TOC entry 3693 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN audit_logs.entity_name; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.entity_name IS 'Entity name (e.g., demand_letter, user, template)';


--
-- TOC entry 3694 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN audit_logs.entity_id; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.entity_id IS 'Entity/Row ID';


--
-- TOC entry 3695 (class 0 OID 0)
-- Dependencies: 245
-- Name: COLUMN audit_logs.changed_fields; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.audit_logs.changed_fields IS 'List of changed field names';


--
-- TOC entry 244 (class 1259 OID 27100)
-- Name: audit_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.audit_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.audit_logs_id_seq OWNER TO postgres;

--
-- TOC entry 3696 (class 0 OID 0)
-- Dependencies: 244
-- Name: audit_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.audit_logs_id_seq OWNED BY public.audit_logs.id;


--
-- TOC entry 221 (class 1259 OID 26878)
-- Name: banks; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.banks (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    code character varying(50) NOT NULL,
    logo_url character varying(500),
    primary_color character varying(20),
    description text,
    active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    deleted_at timestamp with time zone
);


ALTER TABLE public.banks OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 26877)
-- Name: banks_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.banks_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.banks_id_seq OWNER TO postgres;

--
-- TOC entry 3697 (class 0 OID 0)
-- Dependencies: 220
-- Name: banks_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.banks_id_seq OWNED BY public.banks.id;


--
-- TOC entry 250 (class 1259 OID 27181)
-- Name: casbin_rule; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.casbin_rule (
    id integer NOT NULL,
    ptype character varying(255),
    v0 character varying(255),
    v1 character varying(255),
    v2 character varying(255),
    v3 character varying(255),
    v4 character varying(255),
    v5 character varying(255)
);


ALTER TABLE public.casbin_rule OWNER TO postgres;

--
-- TOC entry 249 (class 1259 OID 27180)
-- Name: casbin_rule_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.casbin_rule_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.casbin_rule_id_seq OWNER TO postgres;

--
-- TOC entry 3698 (class 0 OID 0)
-- Dependencies: 249
-- Name: casbin_rule_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.casbin_rule_id_seq OWNED BY public.casbin_rule.id;


--
-- TOC entry 227 (class 1259 OID 26916)
-- Name: departments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.departments (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(20),
    description character varying(255),
    is_active boolean NOT NULL,
    display_order integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.departments OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 26915)
-- Name: departments_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.departments_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.departments_id_seq OWNER TO postgres;

--
-- TOC entry 3699 (class 0 OID 0)
-- Dependencies: 226
-- Name: departments_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.departments_id_seq OWNED BY public.departments.id;


--
-- TOC entry 223 (class 1259 OID 26891)
-- Name: enum_definitions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.enum_definitions (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    display_name character varying(255) NOT NULL,
    description text,
    source_type character varying(50) NOT NULL,
    static_options json,
    table_name character varying(100),
    value_column character varying(100),
    label_column character varying(100),
    filter_conditions json,
    api_url character varying(500),
    api_method character varying(10),
    api_headers json,
    api_transform text,
    custom_query text,
    active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    created_by character varying(100)
);


ALTER TABLE public.enum_definitions OWNER TO postgres;

--
-- TOC entry 222 (class 1259 OID 26890)
-- Name: enum_definitions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.enum_definitions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.enum_definitions_id_seq OWNER TO postgres;

--
-- TOC entry 3700 (class 0 OID 0)
-- Dependencies: 222
-- Name: enum_definitions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.enum_definitions_id_seq OWNED BY public.enum_definitions.id;


--
-- TOC entry 225 (class 1259 OID 26903)
-- Name: field_type_definitions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.field_type_definitions (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    display_name character varying(255) NOT NULL,
    description text,
    base_type character varying(50) NOT NULL,
    schema_definition json NOT NULL,
    validation_rules json,
    strict_type_checking boolean DEFAULT true NOT NULL,
    ui_widget character varying(100),
    ui_options json,
    default_value json,
    active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    created_by character varying(100)
);


ALTER TABLE public.field_type_definitions OWNER TO postgres;

--
-- TOC entry 3701 (class 0 OID 0)
-- Dependencies: 225
-- Name: COLUMN field_type_definitions.strict_type_checking; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.field_type_definitions.strict_type_checking IS 'Whether to enforce strict data type validation';


--
-- TOC entry 224 (class 1259 OID 26902)
-- Name: field_type_definitions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.field_type_definitions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.field_type_definitions_id_seq OWNER TO postgres;

--
-- TOC entry 3702 (class 0 OID 0)
-- Dependencies: 224
-- Name: field_type_definitions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.field_type_definitions_id_seq OWNED BY public.field_type_definitions.id;


--
-- TOC entry 248 (class 1259 OID 27152)
-- Name: file_uploads; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.file_uploads (
    id integer NOT NULL,
    token uuid NOT NULL,
    original_filename character varying(255) NOT NULL,
    storage_path character varying(255) NOT NULL,
    mime_type character varying(100) NOT NULL,
    file_size integer NOT NULL,
    submission_id integer,
    field_id character varying(100) NOT NULL,
    uploaded_at timestamp with time zone DEFAULT now() NOT NULL,
    uploaded_by character varying(100) NOT NULL
);


ALTER TABLE public.file_uploads OWNER TO postgres;

--
-- TOC entry 247 (class 1259 OID 27151)
-- Name: file_uploads_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.file_uploads_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.file_uploads_id_seq OWNER TO postgres;

--
-- TOC entry 3703 (class 0 OID 0)
-- Dependencies: 247
-- Name: file_uploads_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.file_uploads_id_seq OWNED BY public.file_uploads.id;


--
-- TOC entry 243 (class 1259 OID 27075)
-- Name: form_field_mappings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.form_field_mappings (
    id integer NOT NULL,
    template_id integer NOT NULL,
    field_name character varying(100) NOT NULL,
    field_type_id integer,
    enum_definition_id integer
);


ALTER TABLE public.form_field_mappings OWNER TO postgres;

--
-- TOC entry 242 (class 1259 OID 27074)
-- Name: form_field_mappings_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.form_field_mappings_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.form_field_mappings_id_seq OWNER TO postgres;

--
-- TOC entry 3704 (class 0 OID 0)
-- Dependencies: 242
-- Name: form_field_mappings_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.form_field_mappings_id_seq OWNED BY public.form_field_mappings.id;


--
-- TOC entry 241 (class 1259 OID 27038)
-- Name: form_submissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.form_submissions (
    id integer NOT NULL,
    template_id integer NOT NULL,
    fieldman_id character varying(100),
    submitted_by integer,
    status character varying(20) NOT NULL,
    data_json json NOT NULL,
    file_tokens json,
    validation_errors json,
    is_valid boolean NOT NULL,
    reviewed_by integer,
    reviewed_at timestamp with time zone,
    reviewed_comment text,
    validated_by integer,
    validated_on timestamp with time zone,
    submitted_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone
);


ALTER TABLE public.form_submissions OWNER TO postgres;

--
-- TOC entry 3705 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN form_submissions.submitted_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.form_submissions.submitted_by IS 'User ID of submitter (replaces fieldman_id)';


--
-- TOC entry 3706 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN form_submissions.reviewed_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.form_submissions.reviewed_by IS 'User ID of reviewer (approval/rejection)';


--
-- TOC entry 3707 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN form_submissions.validated_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.form_submissions.validated_by IS 'User ID who validated/approved';


--
-- TOC entry 3708 (class 0 OID 0)
-- Dependencies: 241
-- Name: COLUMN form_submissions.validated_on; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.form_submissions.validated_on IS 'Timestamp of validation/approval';


--
-- TOC entry 240 (class 1259 OID 27037)
-- Name: form_submissions_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.form_submissions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.form_submissions_id_seq OWNER TO postgres;

--
-- TOC entry 3709 (class 0 OID 0)
-- Dependencies: 240
-- Name: form_submissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.form_submissions_id_seq OWNED BY public.form_submissions.id;


--
-- TOC entry 233 (class 1259 OID 26964)
-- Name: form_templates; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.form_templates (
    id integer NOT NULL,
    bank_id integer NOT NULL,
    name character varying(255) NOT NULL,
    version character varying(20) NOT NULL,
    form_type character varying(100),
    schema_json json NOT NULL,
    fields json,
    ui_schema json,
    description text,
    active boolean NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone,
    created_by character varying(100)
);


ALTER TABLE public.form_templates OWNER TO postgres;

--
-- TOC entry 232 (class 1259 OID 26963)
-- Name: form_templates_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.form_templates_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.form_templates_id_seq OWNER TO postgres;

--
-- TOC entry 3710 (class 0 OID 0)
-- Dependencies: 232
-- Name: form_templates_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.form_templates_id_seq OWNED BY public.form_templates.id;


--
-- TOC entry 229 (class 1259 OID 26928)
-- Name: locations; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.locations (
    id integer NOT NULL,
    name character varying(100) NOT NULL,
    code character varying(20),
    description character varying(255),
    region character varying(100),
    is_active boolean NOT NULL,
    display_order integer,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.locations OWNER TO postgres;

--
-- TOC entry 228 (class 1259 OID 26927)
-- Name: locations_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.locations_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.locations_id_seq OWNER TO postgres;

--
-- TOC entry 3711 (class 0 OID 0)
-- Dependencies: 228
-- Name: locations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.locations_id_seq OWNED BY public.locations.id;


--
-- TOC entry 237 (class 1259 OID 27004)
-- Name: refresh_tokens; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.refresh_tokens (
    id integer NOT NULL,
    user_id integer NOT NULL,
    token character varying(500) NOT NULL,
    expires_at timestamp with time zone NOT NULL,
    revoked boolean,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.refresh_tokens OWNER TO postgres;

--
-- TOC entry 236 (class 1259 OID 27003)
-- Name: refresh_tokens_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.refresh_tokens_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.refresh_tokens_id_seq OWNER TO postgres;

--
-- TOC entry 3712 (class 0 OID 0)
-- Dependencies: 236
-- Name: refresh_tokens_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.refresh_tokens_id_seq OWNED BY public.refresh_tokens.id;


--
-- TOC entry 217 (class 1259 OID 26855)
-- Name: resource_attributes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.resource_attributes (
    id integer NOT NULL,
    resource_type character varying NOT NULL,
    resource_id character varying NOT NULL,
    attribute_key character varying NOT NULL,
    attribute_value character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.resource_attributes OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 26854)
-- Name: resource_attributes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.resource_attributes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resource_attributes_id_seq OWNER TO postgres;

--
-- TOC entry 3713 (class 0 OID 0)
-- Dependencies: 216
-- Name: resource_attributes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.resource_attributes_id_seq OWNED BY public.resource_attributes.id;


--
-- TOC entry 215 (class 1259 OID 26844)
-- Name: resource_relationships; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.resource_relationships (
    id integer NOT NULL,
    subject_type character varying NOT NULL,
    subject_id character varying NOT NULL,
    resource_type character varying NOT NULL,
    resource_id character varying NOT NULL,
    parent_resource_type character varying NOT NULL,
    parent_resource_id character varying NOT NULL,
    relationship_type character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone
);


ALTER TABLE public.resource_relationships OWNER TO postgres;

--
-- TOC entry 214 (class 1259 OID 26843)
-- Name: resource_relationships_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.resource_relationships_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.resource_relationships_id_seq OWNER TO postgres;

--
-- TOC entry 3714 (class 0 OID 0)
-- Dependencies: 214
-- Name: resource_relationships_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.resource_relationships_id_seq OWNED BY public.resource_relationships.id;


--
-- TOC entry 235 (class 1259 OID 26982)
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    id integer NOT NULL,
    name character varying NOT NULL,
    description character varying,
    permissions json,
    created_at timestamp with time zone DEFAULT now(),
    created_by integer,
    updated_at timestamp with time zone,
    updated_by integer
);


ALTER TABLE public.roles OWNER TO postgres;

--
-- TOC entry 3715 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN roles.created_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.created_by IS 'User ID of creator';


--
-- TOC entry 3716 (class 0 OID 0)
-- Dependencies: 235
-- Name: COLUMN roles.updated_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.roles.updated_by IS 'User ID of last updater';


--
-- TOC entry 234 (class 1259 OID 26981)
-- Name: roles_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.roles_id_seq OWNER TO postgres;

--
-- TOC entry 3717 (class 0 OID 0)
-- Dependencies: 234
-- Name: roles_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_id_seq OWNED BY public.roles.id;


--
-- TOC entry 239 (class 1259 OID 27022)
-- Name: user_attributes; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_attributes (
    id integer NOT NULL,
    user_id integer NOT NULL,
    attribute_key character varying NOT NULL,
    attribute_value character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now()
);


ALTER TABLE public.user_attributes OWNER TO postgres;

--
-- TOC entry 238 (class 1259 OID 27021)
-- Name: user_attributes_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_attributes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_attributes_id_seq OWNER TO postgres;

--
-- TOC entry 3718 (class 0 OID 0)
-- Dependencies: 238
-- Name: user_attributes_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_attributes_id_seq OWNED BY public.user_attributes.id;


--
-- TOC entry 246 (class 1259 OID 27136)
-- Name: user_roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_roles (
    user_id integer NOT NULL,
    role_id integer NOT NULL
);


ALTER TABLE public.user_roles OWNER TO postgres;

--
-- TOC entry 231 (class 1259 OID 26940)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    id integer NOT NULL,
    username character varying NOT NULL,
    email character varying NOT NULL,
    password_hash character varying NOT NULL,
    user_role character varying,
    bank_id integer,
    active boolean,
    is_superuser boolean,
    first_name character varying,
    last_name character varying,
    full_name character varying,
    department character varying,
    level integer,
    location character varying,
    created_at timestamp with time zone DEFAULT now(),
    updated_at timestamp with time zone DEFAULT now(),
    updated_by integer
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 3719 (class 0 OID 0)
-- Dependencies: 231
-- Name: COLUMN users.updated_by; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public.users.updated_by IS 'User ID who last updated this record';


--
-- TOC entry 230 (class 1259 OID 26939)
-- Name: users_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_id_seq OWNER TO postgres;

--
-- TOC entry 3720 (class 0 OID 0)
-- Dependencies: 230
-- Name: users_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_id_seq OWNED BY public.users.id;


--
-- TOC entry 3353 (class 2604 OID 42446)
-- Name: abac_policies id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.abac_policies ALTER COLUMN id SET DEFAULT nextval('public.abac_policies_id_seq'::regclass);


--
-- TOC entry 3380 (class 2604 OID 42447)
-- Name: audit_logs id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs ALTER COLUMN id SET DEFAULT nextval('public.audit_logs_id_seq'::regclass);


--
-- TOC entry 3355 (class 2604 OID 42448)
-- Name: banks id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.banks ALTER COLUMN id SET DEFAULT nextval('public.banks_id_seq'::regclass);


--
-- TOC entry 3384 (class 2604 OID 42449)
-- Name: casbin_rule id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.casbin_rule ALTER COLUMN id SET DEFAULT nextval('public.casbin_rule_id_seq'::regclass);


--
-- TOC entry 3362 (class 2604 OID 42450)
-- Name: departments id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments ALTER COLUMN id SET DEFAULT nextval('public.departments_id_seq'::regclass);


--
-- TOC entry 3357 (class 2604 OID 42451)
-- Name: enum_definitions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enum_definitions ALTER COLUMN id SET DEFAULT nextval('public.enum_definitions_id_seq'::regclass);


--
-- TOC entry 3359 (class 2604 OID 42452)
-- Name: field_type_definitions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.field_type_definitions ALTER COLUMN id SET DEFAULT nextval('public.field_type_definitions_id_seq'::regclass);


--
-- TOC entry 3382 (class 2604 OID 42453)
-- Name: file_uploads id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_uploads ALTER COLUMN id SET DEFAULT nextval('public.file_uploads_id_seq'::regclass);


--
-- TOC entry 3379 (class 2604 OID 42454)
-- Name: form_field_mappings id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_field_mappings ALTER COLUMN id SET DEFAULT nextval('public.form_field_mappings_id_seq'::regclass);


--
-- TOC entry 3377 (class 2604 OID 42455)
-- Name: form_submissions id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_submissions ALTER COLUMN id SET DEFAULT nextval('public.form_submissions_id_seq'::regclass);


--
-- TOC entry 3369 (class 2604 OID 42456)
-- Name: form_templates id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_templates ALTER COLUMN id SET DEFAULT nextval('public.form_templates_id_seq'::regclass);


--
-- TOC entry 3364 (class 2604 OID 42457)
-- Name: locations id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.locations ALTER COLUMN id SET DEFAULT nextval('public.locations_id_seq'::regclass);


--
-- TOC entry 3373 (class 2604 OID 42458)
-- Name: refresh_tokens id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens ALTER COLUMN id SET DEFAULT nextval('public.refresh_tokens_id_seq'::regclass);


--
-- TOC entry 3351 (class 2604 OID 42459)
-- Name: resource_attributes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resource_attributes ALTER COLUMN id SET DEFAULT nextval('public.resource_attributes_id_seq'::regclass);


--
-- TOC entry 3349 (class 2604 OID 42460)
-- Name: resource_relationships id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resource_relationships ALTER COLUMN id SET DEFAULT nextval('public.resource_relationships_id_seq'::regclass);


--
-- TOC entry 3371 (class 2604 OID 42461)
-- Name: roles id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN id SET DEFAULT nextval('public.roles_id_seq'::regclass);


--
-- TOC entry 3375 (class 2604 OID 42462)
-- Name: user_attributes id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_attributes ALTER COLUMN id SET DEFAULT nextval('public.user_attributes_id_seq'::regclass);


--
-- TOC entry 3366 (class 2604 OID 42463)
-- Name: users id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN id SET DEFAULT nextval('public.users_id_seq'::regclass);


--
-- TOC entry 3648 (class 0 OID 26866)
-- Dependencies: 219
-- Data for Name: abac_policies; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.abac_policies VALUES (6, 'Fieldman Draft Management', 'Fieldmen can create, update, submit, and delete their own draft submissions only', '{"condition": "all", "rules": [{"field": "subject.roles", "operator": "==", "value": "fieldman"}, {"field": "resource.owner_id", "operator": "==", "value": {"attribute": "subject.user_id"}}, {"field": "resource.type", "operator": "==", "value": "submission"}, {"field": "resource.status", "operator": "==", "value": "draft"}, {"field": "resource.status", "operator": "==", "value": "submitted"}, {"field": "resource.status", "operator": "==", "value": "approved"}, {"field": "resource.status", "operator": "==", "value": "rejected"}, {"field": "action", "operator": "==", "value": "read"}, {"field": "action", "operator": "==", "value": "create"}, {"field": "action", "operator": "==", "value": "update"}, {"field": "action", "operator": "==", "value": "delete"}, {"field": "action", "operator": "==", "value": "submit"}, {"field": "action", "operator": "==", "value": "review"}]}', true, '2026-02-04 07:56:35.833588+00', '2026-02-04 08:12:52.086453+00');


--
-- TOC entry 3674 (class 0 OID 27101)
-- Dependencies: 245
-- Data for Name: audit_logs; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.audit_logs VALUES (72, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 06:55:32.216361+00', NULL, 'auth', '1', 'null');
INSERT INTO public.audit_logs VALUES (73, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 06:55:39.086363+00', NULL, 'auth', '1', 'null');
INSERT INTO public.audit_logs VALUES (86, 1, 'fieldman2', 'update', 'user', '5', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 5, "username": "fieldman2", "email": "fieldman2@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Tagum", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:04.856124+00:00", "updated_at": "2026-02-03T07:19:53.936580+00:00"}, "after": {"id": 5, "username": "fieldman2", "email": "fieldman2@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Bacolod", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:04.856124+00:00", "updated_at": "2026-02-03T07:19:53.936580+00:00"}}', NULL, 1, NULL, '2026-02-03 07:25:20.217272+00', 'User Management', 'user', '5', '["location"]');
INSERT INTO public.audit_logs VALUES (93, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 08:05:09.917785+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (107, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 23:39:29.218642+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (114, 1, 'supervisor', 'role_updated', 'role', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["roles:read", "forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T00:23:15.216566+00:00", "updated_by": 1}, "after": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T00:23:20.323729+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 00:23:20.341534+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (120, 6, 'fieldman3', 'user_updated', 'user', '6', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 6, "username": "fieldman3", "email": "fieldman3@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Pampanga", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:29.341319+00:00", "updated_at": "2026-02-03T07:08:09.886328+00:00"}, "after": {"id": 6, "username": "fieldman3", "email": "fieldman3@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Pampanga", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:29.341319+00:00", "updated_at": "2026-02-03T07:08:09.886328+00:00"}}', NULL, 1, NULL, '2026-02-04 00:50:47.180922+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (122, 1, 'supervisor', 'role_updated', 'role', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T00:23:20.323729+00:00", "updated_by": 1}, "after": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T00:23:20.323729+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 00:51:09.984976+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (127, 1, 'harrypotter', 'user_updated', 'user', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 1, "username": "harrypotter", "email": "harrypotter@example.com", "user_role": "admin", "department": "Finance", "location": "Makati", "level": 1, "active": true, "bank_id": null, "first_name": "Harry", "last_name": "Potter", "full_name": "Harry Potter", "is_superuser": true, "created_at": "2026-02-02T07:20:24.175792+00:00", "updated_at": "2026-02-04T00:36:50.116058+00:00"}, "after": {"id": 1, "username": "harrypotter", "email": "harrypotter@example.com", "user_role": "admin", "department": "Operations", "location": "Makati", "level": 3, "active": true, "bank_id": null, "first_name": "Harry", "last_name": "Potter", "full_name": "Harry Potter", "is_superuser": true, "created_at": "2026-02-02T07:20:24.175792+00:00", "updated_at": "2026-02-04T00:36:50.116058+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 1, NULL, '2026-02-04 00:59:11.656856+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (128, 1, 'harrypotter', 'user_updated', 'user', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Customer Support", "location": "Bulacan", "level": 2, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T00:58:35.533735+00:00"}, "after": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Operations", "location": "Quezon City", "level": 2, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T00:58:35.533735+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 1, NULL, '2026-02-04 00:59:28.840139+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (129, 1, 'harrypotter', 'user_updated', 'user', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Operations", "location": "Quezon City", "level": 2, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T00:59:28.840139+00:00"}, "after": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "admin", "department": "Operations", "location": "Quezon City", "level": 2, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T00:59:28.840139+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 1, NULL, '2026-02-04 01:00:20.240257+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (74, 1, 'BDO Loan Application Form', 'template_updated', 'template', '12', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 1 fields"}, "after": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, 1, NULL, '2026-02-03 06:56:01.960555+00', NULL, 'template', '12', '[]');
INSERT INTO public.audit_logs VALUES (77, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 07:00:49.449144+00', NULL, 'auth', '1', 'null');
INSERT INTO public.audit_logs VALUES (87, 1, 'admin', 'update', 'user', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "username": "admin", "email": "admin@example.com", "user_role": "admin", "department": "Engineering", "location": "Makati", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-02T07:50:36.536601+00:00", "updated_at": "2026-02-03T00:27:32.577988+00:00"}, "after": {"id": 2, "username": "admin", "email": "admin@example.com", "user_role": "admin", "department": "Engineering", "location": "Makati", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-02T07:50:36.536601+00:00", "updated_at": "2026-02-03T00:27:32.577988+00:00"}}', NULL, 1, NULL, '2026-02-03 07:31:05.273772+00', 'User Management', 'user', '2', '[]');
INSERT INTO public.audit_logs VALUES (23, 1, 'supervisor', 'role_updated', 'role', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": null, "updated_by": 1}, "after": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": null, "updated_by": 1}}', NULL, 1, NULL, '2026-02-02 07:49:11.620013+00', NULL, 'role', '2', NULL);
INSERT INTO public.audit_logs VALUES (24, 1, 'fieldman', 'role_created', 'role', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "created", "after": {"id": 3, "name": "fieldman", "description": "Submit forms and manage own submissions", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update"], "created_at": "2026-02-02T07:50:01.041905+00:00", "created_by": 1, "updated_at": null, "updated_by": 1}}', 1, NULL, NULL, '2026-02-02 07:50:01.056075+00', NULL, 'role', '3', NULL);
INSERT INTO public.audit_logs VALUES (26, 1, 'harrypotter', 'user_updated', 'user', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "username": "harrypotter", "email": "harrypotter@example.com", "user_role": "admin", "department": "Sales", "location": "Makati", "level": 5, "active": true, "bank_id": null, "first_name": "Harry", "last_name": "Potter", "full_name": "Harry Potter", "is_superuser": true, "created_at": "2026-02-02T07:20:24.175792+00:00", "updated_at": "2026-02-02T07:39:56.529915+00:00"}, "after": {"id": 1, "username": "harrypotter", "email": "harrypotter@example.com", "user_role": "admin", "department": "Operations", "location": "Makati", "level": 1, "active": true, "bank_id": null, "first_name": "Harry", "last_name": "Potter", "full_name": "Harry Potter", "is_superuser": true, "created_at": "2026-02-02T07:20:24.175792+00:00", "updated_at": "2026-02-02T07:39:56.529915+00:00"}}', NULL, 1, NULL, '2026-02-02 07:50:43.549213+00', NULL, 'user', '1', NULL);
INSERT INTO public.audit_logs VALUES (94, 1, 'BDO Loan Application Form', 'template_updated', 'template', '12', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}, "after": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, 1, NULL, '2026-02-03 08:05:21.166903+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (108, 1, 'harrypotter', 'update_profile', 'user', '1', 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-03 23:39:53.104874+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (115, 1, 'harrypotter', 'update_profile', 'user', '1', 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-04 00:36:50.116058+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (118, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 00:39:11.085328+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (121, 1, 'BDO Loan Application Form', 'template_updated', 'template', '12', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 2 fields"}, "after": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 2 fields"}}', NULL, 1, NULL, '2026-02-04 00:50:59.352014+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (130, 1, 'supervisor', 'user_updated', 'user', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "admin", "department": "Operations", "location": "Quezon City", "level": 2, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T01:00:20.240257+00:00"}, "after": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "admin", "department": "Customer Support", "location": "Quezon City", "level": 2, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T01:00:20.240257+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 1, NULL, '2026-02-04 01:02:02.570807+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (136, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 01:25:52.758723+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (148, 3, 'supervisor', 'login', 'auth', '3', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 02:25:07.673902+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (153, 1, 'BDO Loan Application Form', 'template_deleted', 'template', '12', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 2 fields"}}', NULL, NULL, 1, '2026-02-04 02:39:17.077252+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (156, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 03:15:35.396152+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (75, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "relationships:create", "relationships:read", "relationships:update", "relationships:delete"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-02T07:21:47.412937+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "relationships:create", "relationships:read", "relationships:update", "relationships:delete"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-02T07:21:47.412937+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-03 06:56:17.36978+00', NULL, 'role', '1', '[]');
INSERT INTO public.audit_logs VALUES (78, 1, 'ddd', 'template_deleted', 'template', '25', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 25, "bank_id": 2, "name": "ddd", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-03 07:01:19.156709+00', NULL, 'template', '25', '["version", "bank_id", "active", "description", "name", "id"]');
INSERT INTO public.audit_logs VALUES (79, 1, 'fieldman1', 'update', 'user', '4', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 4, "username": "fieldman1", "email": "fieldman1@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Quezon City", "level": 1, "active": true, "bank_id": null, "first_name": "John ", "last_name": "Doe", "full_name": "John  Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:43.106727+00:00", "updated_at": "2026-02-03T00:01:35.179499+00:00"}, "after": {"id": 4, "username": "fieldman1", "email": "fieldman1@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Tagum", "level": 1, "active": true, "bank_id": null, "first_name": "John ", "last_name": "Doe", "full_name": "John  Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:43.106727+00:00", "updated_at": "2026-02-03T00:01:35.179499+00:00"}}', NULL, 1, NULL, '2026-02-03 07:02:57.731428+00', 'User Management', 'user', '4', '["location"]');
INSERT INTO public.audit_logs VALUES (88, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 07:34:46.454461+00', NULL, 'auth', '1', 'null');
INSERT INTO public.audit_logs VALUES (95, 1, 'BDO Loan Application Form', 'template_updated', 'template', '12', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 1 fields"}, "after": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 2 fields"}}', NULL, 1, NULL, '2026-02-03 08:10:41.282173+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (99, 1, 'fieldman', 'role_updated', 'role', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 3, "name": "fieldman", "description": "Submit forms and manage own submissions", "permissions": ["roles:read", "forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update"], "created_at": "2026-02-02T07:50:01.041905+00:00", "created_by": 1, "updated_at": "2026-02-03T06:56:25.497388+00:00", "updated_by": 1}, "after": {"id": 3, "name": "fieldman", "description": "Submit forms and manage own submissions", "permissions": ["roles:read", "forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update"], "created_at": "2026-02-02T07:50:01.041905+00:00", "created_by": 1, "updated_at": "2026-02-03T06:56:25.497388+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-03 08:17:46.81815+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (106, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 08:20:26.787375+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (109, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 23:46:36.737961+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (116, 1, 'sample 2', 'template_updated', 'template', '27', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 27, "bank_id": 5, "name": "sample 1", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}, "after": {"id": 27, "bank_id": 5, "name": "sample 2", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, 1, NULL, '2026-02-04 00:37:55.274776+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (131, 1, 'BDO Loan Application Form', 'template_updated', 'template', '12', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 2 fields"}, "after": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 2 fields"}}', NULL, 1, NULL, '2026-02-04 01:02:59.895812+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (132, 1, 'supervisor', 'role_updated', 'role', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T00:23:20.323729+00:00", "updated_by": 1}, "after": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T00:23:20.323729+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 01:03:14.9999+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (133, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 01:03:37.776819+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (19, 1, 'harrypotter', 'update_profile', NULL, NULL, 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-02 07:39:46.40485+00', NULL, 'system', '', NULL);
INSERT INTO public.audit_logs VALUES (20, 1, 'harrypotter', 'update_profile', NULL, NULL, 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-02 07:39:56.529915+00', NULL, 'system', '', NULL);
INSERT INTO public.audit_logs VALUES (76, 1, 'fieldman', 'role_updated', 'role', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 3, "name": "fieldman", "description": "Submit forms and manage own submissions", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update"], "created_at": "2026-02-02T07:50:01.041905+00:00", "created_by": 1, "updated_at": null, "updated_by": 1}, "after": {"id": 3, "name": "fieldman", "description": "Submit forms and manage own submissions", "permissions": ["roles:read", "forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update"], "created_at": "2026-02-02T07:50:01.041905+00:00", "created_by": 1, "updated_at": "2026-02-03T06:56:25.497388+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-03 06:56:25.515626+00', NULL, 'role', '3', '["updated_at", "permissions"]');
INSERT INTO public.audit_logs VALUES (80, 1, 'fieldman3', 'update', 'user', '6', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 6, "username": "fieldman3", "email": "fieldman3@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Bulacan", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:29.341319+00:00", "updated_at": "2026-02-03T00:01:37.023481+00:00"}, "after": {"id": 6, "username": "fieldman3", "email": "fieldman3@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Pampanga", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:29.341319+00:00", "updated_at": "2026-02-03T00:01:37.023481+00:00"}}', NULL, 1, NULL, '2026-02-03 07:08:09.886328+00', 'User Management', 'user', '6', '["location"]');
INSERT INTO public.audit_logs VALUES (89, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 07:49:55.907322+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (96, 2, 'admin', 'user_updated', 'user', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "username": "admin", "email": "admin@example.com", "user_role": "admin", "department": "Engineering", "location": "Makati", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-02T07:50:36.536601+00:00", "updated_at": "2026-02-03T00:27:32.577988+00:00"}, "after": {"id": 2, "username": "admin", "email": "admin@example.com", "user_role": "admin", "department": "Engineering", "location": "Quezon City", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-02T07:50:36.536601+00:00", "updated_at": "2026-02-03T00:27:32.577988+00:00"}}', NULL, 1, NULL, '2026-02-03 08:11:19.074714+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (102, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 08:18:47.063935+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (104, 4, 'fieldman1', 'login', 'auth', '4', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 08:18:58.301748+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (110, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 00:00:00.210465+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (117, 1, 'sample 2', 'template_deleted', 'template', '27', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 27, "bank_id": 5, "name": "sample 2", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-04 00:38:02.685222+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (123, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "relationships:create", "relationships:read", "relationships:update", "relationships:delete"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-02T07:21:47.412937+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "relationships:create", "relationships:read", "relationships:update", "relationships:delete"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-02T07:21:47.412937+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 00:56:23.76015+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (124, 1, 'harrypotter', 'user_updated', 'user', '6', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 6, "username": "fieldman3", "email": "fieldman3@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Pampanga", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:29.341319+00:00", "updated_at": "2026-02-03T07:08:09.886328+00:00"}, "after": {"id": 6, "username": "fieldman3", "email": "fieldman3@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Pampanga", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:29.341319+00:00", "updated_at": "2026-02-03T07:08:09.886328+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 1, NULL, '2026-02-04 00:56:33.401303+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (134, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 01:07:56.372891+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (139, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 01:26:22.793398+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (149, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 02:25:25.797048+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (150, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 02:25:57.4145+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (151, 3, 'supervisor', 'login', 'auth', '3', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 02:26:12.392696+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (13, 1, 'Credit Card Application', 'template_deleted', 'template', '10', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 10, "bank_id": 2, "name": "Credit Card Application", "version": "1.0.0", "form_type": "credit_card", "active": true, "description": "BPI Credit Card Application Form"}}', NULL, NULL, 1, '2026-02-02 07:25:34.884206+00', NULL, 'template', '10', NULL);
INSERT INTO public.audit_logs VALUES (81, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 07:17:27.370005+00', NULL, 'auth', '1', 'null');
INSERT INTO public.audit_logs VALUES (90, 1, 'BDO Loan Application Form', 'template_updated', 'template', '12', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 1 fields"}, "after": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, 1, NULL, '2026-02-03 07:50:13.726268+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (55, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "relationships:create", "relationships:read", "relationships:update", "relationships:delete"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-02T07:21:47.412937+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "relationships:create", "relationships:read", "relationships:update", "relationships:delete"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-02T07:21:47.412937+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-03 01:11:57.01535+00', NULL, 'role', '1', NULL);
INSERT INTO public.audit_logs VALUES (58, 1, 'harrypotter', 'update_profile', 'user', '1', 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-03 01:14:07.836732+00', NULL, 'user', '1', NULL);
INSERT INTO public.audit_logs VALUES (97, 1, 'ddd', 'template_deleted', 'template', '26', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 26, "bank_id": 1, "name": "ddd", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-03 08:12:45.684663+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (98, 2, 'admin', 'user_updated', 'user', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "username": "admin", "email": "admin@example.com", "user_role": "admin", "department": "Engineering", "location": "Quezon City", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-02T07:50:36.536601+00:00", "updated_at": "2026-02-03T08:11:19.074714+00:00"}, "after": {"id": 2, "username": "admin", "email": "admin@example.com", "user_role": "admin", "department": "Legal", "location": "Quezon City", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-02T07:50:36.536601+00:00", "updated_at": "2026-02-03T08:11:19.074714+00:00"}}', NULL, 1, NULL, '2026-02-03 08:14:27.195567+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (100, 4, 'fieldman1', 'login', 'auth', '4', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 08:17:54.038092+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (101, 4, 'fieldman1', 'login', 'auth', '4', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 08:18:05.208292+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (111, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 00:16:05.214522+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (119, 3, 'supervisor', 'user_updated', 'user', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Legal", "location": "General Santos", "level": 1, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-03T01:12:02.879515+00:00"}, "after": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Legal", "location": "Pagadian", "level": 1, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-03T01:12:02.879515+00:00"}}', NULL, 1, NULL, '2026-02-04 00:45:37.288569+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (125, 1, 'harrypotter', 'user_updated', 'user', '6', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 6, "username": "fieldman3", "email": "fieldman3@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Pampanga", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:29.341319+00:00", "updated_at": "2026-02-03T07:08:09.886328+00:00"}, "after": {"id": 6, "username": "fieldman3", "email": "fieldman3@example.com", "user_role": "fieldman", "department": "Operations", "location": "Tagum", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:29.341319+00:00", "updated_at": "2026-02-03T07:08:09.886328+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 1, NULL, '2026-02-04 00:58:22.39243+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (126, 1, 'harrypotter', 'user_updated', 'user', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Legal", "location": "Pagadian", "level": 1, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T00:45:37.288569+00:00"}, "after": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Customer Support", "location": "Bulacan", "level": 2, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T00:45:37.288569+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 1, NULL, '2026-02-04 00:58:35.533735+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (141, 3, 'supervisor', 'login', 'auth', '3', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 01:26:36.977804+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (142, 3, 'supervisor', 'update_profile', 'user', '3', 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-04 01:27:03.540559+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (82, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 07:18:59.705073+00', NULL, 'auth', '1', 'null');
INSERT INTO public.audit_logs VALUES (83, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 07:19:36.560276+00', NULL, 'auth', '1', 'null');
INSERT INTO public.audit_logs VALUES (84, 1, 'fieldman2', 'update', 'user', '5', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 5, "username": "fieldman2", "email": "fieldman2@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Pagadian", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:04.856124+00:00", "updated_at": "2026-02-03T00:01:40.343708+00:00"}, "after": {"id": 5, "username": "fieldman2", "email": "fieldman2@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Tagum", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:04.856124+00:00", "updated_at": "2026-02-03T00:01:40.343708+00:00"}}', NULL, 1, NULL, '2026-02-03 07:19:53.93658+00', 'User Management', 'user', '5', '["location"]');
INSERT INTO public.audit_logs VALUES (91, 2, 'admin', 'user_updated', 'user', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "username": "admin", "email": "admin@example.com", "user_role": "admin", "department": "Engineering", "location": "Makati", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-02T07:50:36.536601+00:00", "updated_at": "2026-02-03T00:27:32.577988+00:00"}, "after": {"id": 2, "username": "admin", "email": "admin@example.com", "user_role": "admin", "department": "Engineering", "location": "Makati", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-02T07:50:36.536601+00:00", "updated_at": "2026-02-03T00:27:32.577988+00:00"}}', NULL, 1, NULL, '2026-02-03 07:50:21.877346+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (180, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:31:27.057228+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (145, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 01:44:33.743697+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (152, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 02:26:21.435174+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (3, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": [], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": null, "updated_by": null}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "relationships:create", "relationships:read", "relationships:update", "relationships:delete"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-02T07:21:47.412937+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-02 07:21:47.432652+00', NULL, 'role', '1', NULL);
INSERT INTO public.audit_logs VALUES (5, 1, 'Credit Card Application', 'template_deleted', 'template', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 1, "bank_id": 1, "name": "Credit Card Application", "version": "1.0.0", "form_type": "credit_card_application", "active": true, "description": "Apply for a BDO credit card"}}', NULL, NULL, 1, '2026-02-02 07:25:04.443502+00', NULL, 'template', '1', NULL);
INSERT INTO public.audit_logs VALUES (6, 1, 'Personal Loan Application', 'template_deleted', 'template', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 2, "bank_id": 1, "name": "Personal Loan Application", "version": "1.0.0", "form_type": "personal_loan_application", "active": true, "description": "Apply for a personal loan from BDO"}}', NULL, NULL, 1, '2026-02-02 07:25:10.174631+00', NULL, 'template', '2', NULL);
INSERT INTO public.audit_logs VALUES (7, 1, 'Savings Account Application', 'template_deleted', 'template', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 3, "bank_id": 2, "name": "Savings Account Application", "version": "1.0.0", "form_type": "savings_account_application", "active": true, "description": "Open a BPI savings account"}}', NULL, NULL, 1, '2026-02-02 07:25:16.216036+00', NULL, 'template', '3', NULL);
INSERT INTO public.audit_logs VALUES (8, 1, 'Auto Loan Application', 'template_deleted', 'template', '4', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 4, "bank_id": 2, "name": "Auto Loan Application", "version": "1.0.0", "form_type": "auto_loan_application", "active": true, "description": "Finance your dream car with BPI"}}', NULL, NULL, 1, '2026-02-02 07:25:18.709468+00', NULL, 'template', '4', NULL);
INSERT INTO public.audit_logs VALUES (9, 1, 'Home Loan Application', 'template_deleted', 'template', '5', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 5, "bank_id": 3, "name": "Home Loan Application", "version": "1.0.0", "form_type": "home_loan_application", "active": true, "description": "Housing loan application for Metrobank"}}', NULL, NULL, 1, '2026-02-02 07:25:21.328175+00', NULL, 'template', '5', NULL);
INSERT INTO public.audit_logs VALUES (10, 1, 'Business Loan Application', 'template_deleted', 'template', '6', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 6, "bank_id": 3, "name": "Business Loan Application", "version": "1.0.0", "form_type": "business_loan_application", "active": true, "description": "Small and Medium Enterprise (SME) loan application"}}', NULL, NULL, 1, '2026-02-02 07:25:23.737804+00', NULL, 'template', '6', NULL);
INSERT INTO public.audit_logs VALUES (11, 1, 'Time Deposit Application', 'template_deleted', 'template', '7', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 7, "bank_id": 4, "name": "Time Deposit Application", "version": "1.0.0", "form_type": "time_deposit_application", "active": true, "description": "Open a time deposit account"}}', NULL, NULL, 1, '2026-02-02 07:25:26.317514+00', NULL, 'template', '7', NULL);
INSERT INTO public.audit_logs VALUES (12, 1, 'Housing Loan Application', 'template_deleted', 'template', '9', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 9, "bank_id": 1, "name": "Housing Loan Application", "version": "1.0.0", "form_type": "housing_loan", "active": true, "description": "BDO Unibank Housing Loan Application with nested conditionals"}}', NULL, NULL, 1, '2026-02-02 07:25:31.482289+00', NULL, 'template', '9', NULL);
INSERT INTO public.audit_logs VALUES (18, 1, 'harrypotter', 'update_profile', NULL, NULL, 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-02 07:39:42.643147+00', NULL, 'system', '', NULL);
INSERT INTO public.audit_logs VALUES (21, 1, 'BDO Loan Application Form', 'template_updated', 'template', '12', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}, "after": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, 1, NULL, '2026-02-02 07:40:31.975835+00', NULL, 'template', '12', NULL);
INSERT INTO public.audit_logs VALUES (22, 1, 'supervisor', 'role_created', 'role', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "created", "after": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": null, "updated_by": 1}}', 1, NULL, NULL, '2026-02-02 07:49:05.902784+00', NULL, 'role', '2', NULL);
INSERT INTO public.audit_logs VALUES (25, 2, 'admin', 'user_created', 'user', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "created", "after": {"id": 2, "username": "admin", "email": "admin@example.com", "user_role": "admin", "department": "Engineering", "location": "Makati", "level": 1, "active": true, "role": "admin", "is_active": true, "roles": ["admin"]}}', 1, NULL, NULL, '2026-02-02 07:50:36.536601+00', NULL, 'user', '2', NULL);
INSERT INTO public.audit_logs VALUES (28, 3, 'supervisor', 'user_created', 'user', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "created", "after": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Legal", "location": "Tagum", "level": 1, "active": true, "role": "supervisor", "is_active": true, "roles": ["supervisor"]}}', 1, NULL, NULL, '2026-02-03 00:00:09.962869+00', NULL, 'user', '3', NULL);
INSERT INTO public.audit_logs VALUES (29, 4, 'fieldman1', 'user_created', 'user', '4', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "created", "after": {"id": 4, "username": "fieldman1", "email": "fieldman1@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Quezon City", "level": 1, "active": true, "role": "fieldman", "is_active": true, "roles": ["fieldman"]}}', 1, NULL, NULL, '2026-02-03 00:00:43.106727+00', NULL, 'user', '4', NULL);
INSERT INTO public.audit_logs VALUES (30, 5, 'fieldman2', 'user_created', 'user', '5', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "created", "after": {"id": 5, "username": "fieldman2", "email": "fieldman2@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Paranaque", "level": 1, "active": true, "role": "fieldman", "is_active": true, "roles": ["fieldman"]}}', 1, NULL, NULL, '2026-02-03 00:01:04.856124+00', NULL, 'user', '5', NULL);
INSERT INTO public.audit_logs VALUES (31, 6, 'fieldman3', 'user_created', 'user', '6', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "created", "after": {"id": 6, "username": "fieldman3", "email": "fieldman3@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Bulacan", "level": 1, "active": true, "role": "fieldman", "is_active": true, "roles": ["fieldman"]}}', 1, NULL, NULL, '2026-02-03 00:01:29.341319+00', NULL, 'user', '6', NULL);
INSERT INTO public.audit_logs VALUES (32, 3, 'supervisor', 'user_updated', 'user', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Legal", "location": "Tagum", "level": 1, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-03T00:00:09.962869+00:00"}, "after": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Legal", "location": "Tagum", "level": 1, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-03T00:00:09.962869+00:00"}}', NULL, 1, NULL, '2026-02-03 00:01:33.110477+00', NULL, 'user', '3', NULL);
INSERT INTO public.audit_logs VALUES (33, 4, 'fieldman1', 'user_updated', 'user', '4', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 4, "username": "fieldman1", "email": "fieldman1@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Quezon City", "level": 1, "active": true, "bank_id": null, "first_name": "John ", "last_name": "Doe", "full_name": "John  Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:43.106727+00:00", "updated_at": "2026-02-03T00:00:43.106727+00:00"}, "after": {"id": 4, "username": "fieldman1", "email": "fieldman1@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Quezon City", "level": 1, "active": true, "bank_id": null, "first_name": "John ", "last_name": "Doe", "full_name": "John  Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:43.106727+00:00", "updated_at": "2026-02-03T00:00:43.106727+00:00"}}', NULL, 1, NULL, '2026-02-03 00:01:35.179499+00', NULL, 'user', '4', NULL);
INSERT INTO public.audit_logs VALUES (34, 6, 'fieldman3', 'user_updated', 'user', '6', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 6, "username": "fieldman3", "email": "fieldman3@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Bulacan", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:29.341319+00:00", "updated_at": "2026-02-03T00:01:29.341319+00:00"}, "after": {"id": 6, "username": "fieldman3", "email": "fieldman3@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Bulacan", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:29.341319+00:00", "updated_at": "2026-02-03T00:01:29.341319+00:00"}}', NULL, 1, NULL, '2026-02-03 00:01:37.023481+00', NULL, 'user', '6', NULL);
INSERT INTO public.audit_logs VALUES (35, 5, 'fieldman2', 'user_updated', 'user', '5', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 5, "username": "fieldman2", "email": "fieldman2@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Paranaque", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:04.856124+00:00", "updated_at": "2026-02-03T00:01:04.856124+00:00"}, "after": {"id": 5, "username": "fieldman2", "email": "fieldman2@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Pagadian", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:04.856124+00:00", "updated_at": "2026-02-03T00:01:04.856124+00:00"}}', NULL, 1, NULL, '2026-02-03 00:01:40.343708+00', NULL, 'user', '5', NULL);
INSERT INTO public.audit_logs VALUES (37, 1, 'harrypotter', 'update_profile', NULL, NULL, 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-03 00:14:35.810164+00', NULL, 'system', '', NULL);
INSERT INTO public.audit_logs VALUES (39, 1, 'BDO Loan Application Form', 'template_updated', 'template', '12', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 1 fields"}, "after": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, 1, NULL, '2026-02-03 00:24:12.855659+00', NULL, 'template', '12', NULL);
INSERT INTO public.audit_logs VALUES (40, 2, 'admin', 'user_updated', 'user', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "username": "admin", "email": "admin@example.com", "user_role": "admin", "department": "Engineering", "location": "Makati", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-02T07:50:36.536601+00:00", "updated_at": "2026-02-02T07:50:36.536601+00:00"}, "after": {"id": 2, "username": "admin", "email": "admin@example.com", "user_role": "admin", "department": "Engineering", "location": "Makati", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-02T07:50:36.536601+00:00", "updated_at": "2026-02-02T07:50:36.536601+00:00"}}', NULL, 1, NULL, '2026-02-03 00:27:32.577988+00', NULL, 'user', '2', NULL);
INSERT INTO public.audit_logs VALUES (41, 1, 'BDO Loan Application Form', 'template_updated', 'template', '12', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}, "after": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, 1, NULL, '2026-02-03 00:27:44.82618+00', NULL, 'template', '12', NULL);
INSERT INTO public.audit_logs VALUES (42, 1, 'fieldman', 'role_updated', 'role', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 3, "name": "fieldman", "description": "Submit forms and manage own submissions", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update"], "created_at": "2026-02-02T07:50:01.041905+00:00", "created_by": 1, "updated_at": null, "updated_by": 1}, "after": {"id": 3, "name": "fieldman", "description": "Submit forms and manage own submissions", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update"], "created_at": "2026-02-02T07:50:01.041905+00:00", "created_by": 1, "updated_at": null, "updated_by": 1}}', NULL, 1, NULL, '2026-02-03 00:27:56.310915+00', NULL, 'role', '3', NULL);
INSERT INTO public.audit_logs VALUES (43, 1, 'Personal Loan Application', 'template_deleted', 'template', '14', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 14, "bank_id": 5, "name": "Personal Loan Application", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-03 00:44:13.304356+00', NULL, 'template', '14', NULL);
INSERT INTO public.audit_logs VALUES (44, 1, 'Personal Loan Application', 'template_deleted', 'template', '15', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 15, "bank_id": 5, "name": "Personal Loan Application", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-03 00:49:07.945669+00', NULL, 'template', '15', NULL);
INSERT INTO public.audit_logs VALUES (46, 1, 'Personal Loan Application', 'template_deleted', 'template', '16', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 16, "bank_id": 4, "name": "Personal Loan Application", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-03 00:50:09.426103+00', NULL, 'template', '16', NULL);
INSERT INTO public.audit_logs VALUES (47, 1, 'Auto Loan Application', 'template_deleted', 'template', '18', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 18, "bank_id": 3, "name": "Auto Loan Application", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-03 00:55:00.249788+00', NULL, 'template', '18', NULL);
INSERT INTO public.audit_logs VALUES (48, 1, 'sample', 'template_deleted', 'template', '20', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 20, "bank_id": 3, "name": "sample", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-03 00:58:46.294612+00', NULL, 'template', '20', NULL);
INSERT INTO public.audit_logs VALUES (49, 1, 'sample', 'template_deleted', 'template', '19', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 19, "bank_id": 3, "name": "sample", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-03 00:58:54.188906+00', NULL, 'template', '19', NULL);
INSERT INTO public.audit_logs VALUES (50, 1, 'sample', 'template_deleted', 'template', '21', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 21, "bank_id": 3, "name": "sample", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-03 01:02:28.739439+00', NULL, 'template', '21', NULL);
INSERT INTO public.audit_logs VALUES (51, 1, 'sample', 'template_deleted', 'template', '22', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 22, "bank_id": 3, "name": "sample", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-03 01:03:03.658146+00', NULL, 'template', '22', NULL);
INSERT INTO public.audit_logs VALUES (52, 1, 'sample', 'template_deleted', 'template', '23', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 23, "bank_id": 3, "name": "sample", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-03 01:04:48.955677+00', NULL, 'template', '23', NULL);
INSERT INTO public.audit_logs VALUES (53, 1, 'sample', 'template_deleted', 'template', '24', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 24, "bank_id": 3, "name": "sample", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-03 01:05:22.873795+00', NULL, 'template', '24', NULL);
INSERT INTO public.audit_logs VALUES (146, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 02:07:25.001389+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (155, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 02:43:27.533127+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (54, 1, 'BDO Loan Application Form', 'template_updated', 'template', '12', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 1 fields"}, "after": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, 1, NULL, '2026-02-03 01:11:50.360402+00', NULL, 'template', '12', NULL);
INSERT INTO public.audit_logs VALUES (56, 3, 'supervisor', 'user_updated', 'user', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Legal", "location": "Tagum", "level": 1, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-03T00:01:33.110477+00:00"}, "after": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Legal", "location": "General Santos", "level": 1, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-03T00:01:33.110477+00:00"}}', NULL, 1, NULL, '2026-02-03 01:12:02.879515+00', NULL, 'user', '3', NULL);
INSERT INTO public.audit_logs VALUES (59, 1, 'harrypotter', 'update_profile', 'user', '1', 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-03 01:14:13.874465+00', NULL, 'user', '1', NULL);
INSERT INTO public.audit_logs VALUES (62, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 01:20:28.778628+00', NULL, 'auth', '1', NULL);
INSERT INTO public.audit_logs VALUES (63, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 01:20:47.954347+00', NULL, 'auth', '1', NULL);
INSERT INTO public.audit_logs VALUES (64, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 01:53:02.81647+00', NULL, 'auth', '1', NULL);
INSERT INTO public.audit_logs VALUES (65, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 05:18:35.750515+00', NULL, 'auth', '1', NULL);
INSERT INTO public.audit_logs VALUES (66, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 05:18:37.724076+00', NULL, 'auth', '1', NULL);
INSERT INTO public.audit_logs VALUES (67, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 05:18:39.851943+00', NULL, 'auth', '1', NULL);
INSERT INTO public.audit_logs VALUES (68, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 05:26:56.578612+00', NULL, 'auth', '1', NULL);
INSERT INTO public.audit_logs VALUES (69, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 05:39:56.26151+00', NULL, 'auth', '1', NULL);
INSERT INTO public.audit_logs VALUES (70, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 06:08:10.86537+00', NULL, 'auth', '1', NULL);
INSERT INTO public.audit_logs VALUES (71, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-03 06:31:16.482979+00', NULL, 'auth', '1', NULL);
INSERT INTO public.audit_logs VALUES (85, 1, 'fieldman2', 'update', 'user', '5', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 5, "username": "fieldman2", "email": "fieldman2@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Tagum", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:04.856124+00:00", "updated_at": "2026-02-03T07:19:53.936580+00:00"}, "after": {"id": 5, "username": "fieldman2", "email": "fieldman2@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Tagum", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:04.856124+00:00", "updated_at": "2026-02-03T07:19:53.936580+00:00"}}', NULL, 1, NULL, '2026-02-03 07:24:16.665268+00', 'User Management', 'user', '5', '[]');
INSERT INTO public.audit_logs VALUES (92, 2, 'admin', 'user_updated', 'user', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "username": "admin", "email": "admin@example.com", "user_role": "admin", "department": "Engineering", "location": "Makati", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-02T07:50:36.536601+00:00", "updated_at": "2026-02-03T00:27:32.577988+00:00"}, "after": {"id": 2, "username": "admin", "email": "admin@example.com", "user_role": "admin", "department": "Engineering", "location": "Makati", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-02T07:50:36.536601+00:00", "updated_at": "2026-02-03T00:27:32.577988+00:00"}}', NULL, 1, NULL, '2026-02-03 08:04:48.195219+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (103, 1, 'fieldman', 'role_updated', 'role', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 3, "name": "fieldman", "description": "Submit forms and manage own submissions", "permissions": ["roles:read", "forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update"], "created_at": "2026-02-02T07:50:01.041905+00:00", "created_by": 1, "updated_at": "2026-02-03T06:56:25.497388+00:00", "updated_by": 1}, "after": {"id": 3, "name": "fieldman", "description": "Submit forms and manage own submissions", "permissions": ["users:read", "roles:read", "forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update"], "created_at": "2026-02-02T07:50:01.041905+00:00", "created_by": 1, "updated_at": "2026-02-03T08:18:52.780766+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-03 08:18:52.803646+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (105, 4, 'fieldman1', 'update_profile', 'user', '4', 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-03 08:19:15.046848+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (113, 1, 'supervisor', 'role_updated', 'role', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": null, "updated_by": 1}, "after": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["roles:read", "forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T00:23:15.216566+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 00:23:15.237185+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (135, 1, 'Auto Loan Application', 'template_updated', 'template', '13', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 13, "bank_id": 2, "name": "Auto Loan Application", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}, "after": {"id": 13, "bank_id": 2, "name": "Auto Loan Application", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 2 fields"}}', NULL, 1, NULL, '2026-02-04 01:08:06.554486+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (147, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 02:24:05.584298+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (137, 1, 'fieldman2', 'user_updated', 'user', '5', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 5, "username": "fieldman2", "email": "fieldman2@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Bacolod", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:04.856124+00:00", "updated_at": "2026-02-03T07:25:20.217272+00:00"}, "after": {"id": 5, "username": "fieldman2", "email": "fieldman2@example.com", "user_role": "fieldman", "department": "Customer Support", "location": "Bacolod", "level": 1, "active": true, "bank_id": null, "first_name": "John", "last_name": "Doe", "full_name": "John Doe", "is_superuser": false, "created_at": "2026-02-03T00:01:04.856124+00:00", "updated_at": "2026-02-03T07:25:20.217272+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 1, NULL, '2026-02-04 01:25:59.580936+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (138, 3, 'supervisor', 'login', 'auth', '3', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 01:26:08.039218+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (143, 3, 'supervisor', 'update_profile', 'user', '3', 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-04 01:27:11.912048+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (144, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 01:27:18.120774+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (183, 1, 'BDO Loan Application Form', 'template_updated', 'template', '12', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 2 fields"}, "after": {"id": 12, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 2 fields"}}', NULL, 1, NULL, '2026-02-04 06:33:30.999842+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (185, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:26:44.115814+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:26:44.115814+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 06:33:53.385323+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (190, 3, 'supervisor', 'login', 'auth', '3', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:34:59.040053+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (191, 2, 'admin', 'login', 'auth', '2', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:35:23.192049+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (192, 2, 'supervisor', 'role_updated', 'role', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T03:47:01.409415+00:00", "updated_by": 1}, "after": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T06:35:42.438833+00:00", "updated_by": 2}}', NULL, 2, NULL, '2026-02-04 06:35:42.462153+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (197, 2, 'admin', 'login', 'auth', '2', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:36:24.365745+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (198, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:36:53.777681+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (206, 1, 'Personal Loan Application', 'template_deleted', 'template', '17', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 17, "bank_id": 4, "name": "Personal Loan Application", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-04 07:00:54.281403+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (215, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 07:28:40.405915+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (224, 4, 'fieldman1', 'login', 'auth', '4', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 08:15:57.329541+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (225, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 08:16:43.800687+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (140, 1, 'supervisor', 'user_updated', 'user', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "admin", "department": "Customer Support", "location": "Quezon City", "level": 2, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T01:02:02.570807+00:00"}, "after": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Customer Support", "location": "Quezon City", "level": 2, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T01:02:02.570807+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 1, NULL, '2026-02-04 01:26:30.516882+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (178, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:26:44.115814+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:26:44.115814+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 06:29:22.019787+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (184, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:26:44.115814+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:26:44.115814+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 06:33:49.45864+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (189, 2, 'supervisor', 'user_updated', 'user', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Customer Support", "location": "Davao", "level": 2, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T06:33:16.879378+00:00"}, "after": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Customer Support", "location": "Paranaque", "level": 2, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T06:33:16.879378+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 2, NULL, '2026-02-04 06:34:50.288717+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (194, 3, 'supervisor', 'login', 'auth', '3', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:35:52.447613+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (195, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:36:11.785511+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (199, 2, 'admin', 'login', 'auth', '2', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:37:48.276766+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (201, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:38:34.852454+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (154, 1, 'Personal Loan Application', 'template_deleted', 'template', '17', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "deleted", "before": {"id": 17, "bank_id": 4, "name": "Personal Loan Application", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, NULL, 1, '2026-02-04 02:39:23.779479+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (181, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:31:28.220291+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (182, 1, 'supervisor', 'user_updated', 'user', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Customer Support", "location": "Quezon City", "level": 2, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T01:27:11.912048+00:00"}, "after": {"id": 3, "username": "supervisor", "email": "supervisor@example.com", "user_role": "supervisor", "department": "Customer Support", "location": "Davao", "level": 2, "active": true, "bank_id": null, "first_name": "Jane", "last_name": "Doe", "full_name": "Jane Doe", "is_superuser": false, "created_at": "2026-02-03T00:00:09.962869+00:00", "updated_at": "2026-02-04T01:27:11.912048+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 1, NULL, '2026-02-04 06:33:16.879378+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (186, 1, 'harrypotter', 'update_profile', 'user', '1', 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-04 06:34:14.102537+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (187, 2, 'admin', 'login', 'auth', '2', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:34:28.374946+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (188, 2, 'admin', 'login', 'auth', '2', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:34:43.938999+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (200, 3, 'supervisor', 'login', 'auth', '3', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:38:00.743041+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (208, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 07:12:00.342051+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (220, 4, 'fieldman1', 'login', 'auth', '4', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 08:07:33.916579+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (223, 5, 'fieldman2', 'login', 'auth', '5', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 08:13:42.852427+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (157, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 03:41:03.643199+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (158, 3, 'supervisor', 'login', 'auth', '3', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 03:43:02.320398+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (159, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 03:43:24.183119+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (160, 1, 'supervisor', 'role_updated', 'role', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T00:23:20.323729+00:00", "updated_by": 1}, "after": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T00:23:20.323729+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 03:43:36.854412+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (161, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "relationships:create", "relationships:read", "relationships:update", "relationships:delete"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-02T07:21:47.412937+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T03:44:16.394541+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 03:44:16.438459+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (162, 3, 'supervisor', 'login', 'auth', '3', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 03:44:27.07643+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (163, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 03:46:42.436344+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (164, 1, 'supervisor', 'role_updated', 'role', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T00:23:20.323729+00:00", "updated_by": 1}, "after": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T03:47:01.409415+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 03:47:01.457267+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (165, 3, 'supervisor', 'login', 'auth', '3', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 03:47:11.500963+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (166, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 03:47:37.909784+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (167, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 05:08:31.914199+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (168, 1, 'BDO Loan Application Form', 'template_updated', 'template', '28', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 28, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}, "after": {"id": 28, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, 1, NULL, '2026-02-04 05:18:19.413657+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (169, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 05:24:37.996624+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (170, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 05:45:21.062488+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (171, 1, 'harrypotter', 'update_profile', 'user', '1', 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-04 05:49:08.837433+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (172, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T03:44:16.394541+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "submissions:submit", "submissions:read", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T05:59:13.889298+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 05:59:13.908201+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (173, 2, 'admin', 'login', 'auth', '2', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 05:59:29.19873+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (174, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 05:59:53.107137+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (177, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:00:42.412394+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (203, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:47:01.717393+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (213, 1, 'harrypotter', 'update_profile', 'user', '1', 'success', NULL, NULL, 'null', '"User updated their profile"', 'null', NULL, NULL, NULL, '2026-02-04 07:14:06.598602+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (175, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "submissions:submit", "submissions:read", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T05:59:13.889298+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "submissions:submit", "submissions:read", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T05:59:13.889298+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 06:00:04.641113+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (176, 2, 'admin', 'login', 'auth', '2', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 06:00:13.489214+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (179, 1, 'fieldman', 'role_updated', 'role', '3', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 3, "name": "fieldman", "description": "Submit forms and manage own submissions", "permissions": ["users:read", "roles:read", "forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update"], "created_at": "2026-02-02T07:50:01.041905+00:00", "created_by": 1, "updated_at": "2026-02-03T08:18:52.780766+00:00", "updated_by": 1}, "after": {"id": 3, "name": "fieldman", "description": "Submit forms and manage own submissions", "permissions": ["users:read", "roles:read", "forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update"], "created_at": "2026-02-02T07:50:01.041905+00:00", "created_by": 1, "updated_at": "2026-02-03T08:18:52.780766+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 06:29:35.516924+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (196, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:26:44.115814+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:36:18.903178+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 06:36:18.932866+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (202, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:36:18.903178+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:38:44.048269+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 06:38:44.069638+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (204, 1, 'harrypotter', 'user_updated', 'user', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 1, "username": "harrypotter", "email": "harrypotter@example.com", "user_role": "admin", "department": "Legal", "location": "Makati", "level": 3, "active": true, "bank_id": null, "first_name": "Harry", "last_name": "Potter", "full_name": "Harry Potter", "is_superuser": true, "created_at": "2026-02-02T07:20:24.175792+00:00", "updated_at": "2026-02-04T06:34:14.102537+00:00"}, "after": {"id": 1, "username": "harrypotter", "email": "harrypotter@example.com", "user_role": "admin", "department": "Legal", "location": "Makati", "level": 3, "active": true, "bank_id": null, "first_name": "Harry", "last_name": "Potter", "full_name": "Harry Potter", "is_superuser": true, "created_at": "2026-02-02T07:20:24.175792+00:00", "updated_at": "2026-02-04T06:34:14.102537+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 1, NULL, '2026-02-04 06:47:07.700105+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (205, 1, 'harrypotter', 'user_updated', 'user', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 1, "username": "harrypotter", "email": "harrypotter@example.com", "user_role": "admin", "department": "Legal", "location": "Makati", "level": 3, "active": true, "bank_id": null, "first_name": "Harry", "last_name": "Potter", "full_name": "Harry Potter", "is_superuser": true, "created_at": "2026-02-02T07:20:24.175792+00:00", "updated_at": "2026-02-04T06:34:14.102537+00:00"}, "after": {"id": 1, "username": "harrypotter", "email": "harrypotter@example.com", "user_role": "admin", "department": "Legal", "location": "Makati", "level": 3, "active": true, "bank_id": null, "first_name": "Harry", "last_name": "Potter", "full_name": "Harry Potter", "is_superuser": true, "created_at": "2026-02-02T07:20:24.175792+00:00", "updated_at": "2026-02-04T06:34:14.102537+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 1, NULL, '2026-02-04 07:00:40.353928+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (207, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:38:44.048269+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:38:44.048269+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 07:00:59.545919+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (214, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 07:15:11.059939+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (222, 4, 'fieldman1', 'login', 'auth', '4', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 08:13:00.960207+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (209, 1, 'harrypotter', 'user_updated', 'user', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', NULL, NULL, '{"before": {"id": 1, "username": "harrypotter", "email": "harrypotter@example.com", "user_role": "admin", "department": "Legal", "location": "Makati", "level": 3, "active": true, "bank_id": null, "first_name": "Harry", "last_name": "Potter", "full_name": "Harry Potter", "is_superuser": true, "created_at": "2026-02-02T07:20:24.175792+00:00", "updated_at": "2026-02-04T06:34:14.102537+00:00"}, "after": {"id": 1, "username": "harrypotter", "email": "harrypotter@example.com", "user_role": "admin", "department": "Legal", "location": "Makati", "level": 3, "active": true, "bank_id": null, "first_name": "Harry", "last_name": "Potter", "full_name": "Harry Potter", "is_superuser": true, "created_at": "2026-02-02T07:20:24.175792+00:00", "updated_at": "2026-02-04T06:34:14.102537+00:00"}, "edited_fields": ["email", "user_role", "active", "department", "location", "first_name", "last_name", "level"]}', NULL, 1, NULL, '2026-02-04 07:13:21.302113+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (212, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:38:44.048269+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:38:44.048269+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 07:13:53.642832+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (210, 1, 'BDO Loan Application Form', 'template_updated', 'template', '28', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 28, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.0", "form_type": null, "active": true, "description": "Form template created with 1 fields"}, "after": {"id": 28, "bank_id": 1, "name": "BDO Loan Application Form", "version": "1.1", "form_type": null, "active": true, "description": "Form template created with 1 fields"}}', NULL, 1, NULL, '2026-02-04 07:13:32.396774+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (211, 1, 'admin', 'role_updated', 'role', '1', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:38:44.048269+00:00", "updated_by": 1}, "after": {"id": 1, "name": "admin", "description": "Administrator", "permissions": ["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"], "created_at": "2026-02-02T07:20:24.175792+00:00", "created_by": null, "updated_at": "2026-02-04T06:38:44.048269+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 07:13:49.833232+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (216, 1, 'supervisor', 'role_updated', 'role', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T06:35:42.438833+00:00", "updated_by": 2}, "after": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T07:38:13.389065+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 07:38:13.425287+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (217, 3, 'supervisor', 'login', 'auth', '3', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 07:38:18.584985+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (218, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 07:38:31.43714+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (219, 1, 'supervisor', 'role_updated', 'role', '2', 'success', '127.0.0.1', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/144.0.0.0 Safari/537.36', 'null', 'null', '{"action": "updated", "before": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T07:38:13.389065+00:00", "updated_by": 1}, "after": {"id": 2, "name": "supervisor", "description": "Review and approve submissions for their bank", "permissions": ["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review"], "created_at": "2026-02-02T07:49:05.887430+00:00", "created_by": 1, "updated_at": "2026-02-04T07:38:13.389065+00:00", "updated_by": 1}}', NULL, 1, NULL, '2026-02-04 08:07:15.735164+00', NULL, NULL, NULL, NULL);
INSERT INTO public.audit_logs VALUES (221, 1, 'harrypotter', 'login', 'auth', '1', 'success', NULL, NULL, 'null', '"Login success"', 'null', NULL, NULL, NULL, '2026-02-04 08:08:00.924002+00', NULL, NULL, NULL, NULL);


--
-- TOC entry 3650 (class 0 OID 26878)
-- Dependencies: 221
-- Data for Name: banks; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.banks VALUES (1, 'Banco de Oro', 'BDO', NULL, NULL, 'Banco de Oro - Demo Bank', true, '2026-02-02 07:18:52.85778+00', NULL, NULL);
INSERT INTO public.banks VALUES (2, 'Bank of the Philippine Islands', 'BPI', NULL, NULL, 'Bank of the Philippine Islands - Demo Bank', true, '2026-02-02 07:18:52.868598+00', NULL, NULL);
INSERT INTO public.banks VALUES (3, 'Metropolitan Bank & Trust Company', 'METROBANK', NULL, NULL, 'Metropolitan Bank & Trust Company - Demo Bank', true, '2026-02-02 07:18:52.904175+00', NULL, NULL);
INSERT INTO public.banks VALUES (4, 'Security Bank Corporation', 'SECURITYBANK', NULL, NULL, 'Security Bank Corporation - Demo Bank', true, '2026-02-02 07:18:52.921431+00', NULL, NULL);
INSERT INTO public.banks VALUES (5, 'Rizal Commercial Banking Corporation', 'RCBC', NULL, NULL, 'Rizal Commercial Banking Corporation - Demo Bank', true, '2026-02-02 07:18:52.945816+00', NULL, NULL);


--
-- TOC entry 3679 (class 0 OID 27181)
-- Dependencies: 250
-- Data for Name: casbin_rule; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.casbin_rule VALUES (8254, 'p', 'fieldman', 'users', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8255, 'p', 'fieldman', 'roles', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8256, 'p', 'fieldman', 'forms', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8257, 'p', 'fieldman', 'templates', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8258, 'p', 'fieldman', 'submissions', 'create', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8259, 'p', 'fieldman', 'submissions', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8260, 'p', 'fieldman', 'submissions', 'update', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8261, 'p', 'admin', 'users', 'create', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8262, 'p', 'admin', 'users', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8263, 'p', 'admin', 'users', 'update', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8264, 'p', 'admin', 'users', 'delete', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8265, 'p', 'admin', 'roles', 'create', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8266, 'p', 'admin', 'roles', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8267, 'p', 'admin', 'roles', 'update', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8268, 'p', 'admin', 'roles', 'delete', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8269, 'p', 'admin', 'forms', 'create', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8270, 'p', 'admin', 'forms', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8271, 'p', 'admin', 'forms', 'update', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8272, 'p', 'admin', 'forms', 'delete', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8273, 'p', 'admin', 'templates', 'create', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8274, 'p', 'admin', 'templates', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8275, 'p', 'admin', 'templates', 'update', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8276, 'p', 'admin', 'templates', 'delete', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8277, 'p', 'admin', 'submissions', 'create', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8278, 'p', 'admin', 'submissions', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8279, 'p', 'admin', 'submissions', 'viewDetails', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8280, 'p', 'admin', 'submissions', 'update', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8281, 'p', 'admin', 'submissions', 'delete', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8282, 'p', 'admin', 'submissions', 'review', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8283, 'p', 'admin', 'banks', 'create', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8284, 'p', 'admin', 'banks', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8285, 'p', 'admin', 'banks', 'update', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8286, 'p', 'admin', 'banks', 'delete', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8287, 'p', 'admin', 'policies', 'create', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8288, 'p', 'admin', 'policies', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8289, 'p', 'admin', 'policies', 'update', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8290, 'p', 'admin', 'policies', 'delete', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8291, 'p', 'admin', 'system', 'configure', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8292, 'p', 'supervisor', 'forms', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8293, 'p', 'supervisor', 'templates', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8294, 'p', 'supervisor', 'submissions', 'create', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8295, 'p', 'supervisor', 'submissions', 'read', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8296, 'p', 'supervisor', 'submissions', 'viewDetails', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8297, 'p', 'supervisor', 'submissions', 'update', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8298, 'p', 'supervisor', 'submissions', 'delete', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8299, 'p', 'supervisor', 'submissions', 'review', NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8300, 'g', 'fieldman3', 'fieldman', NULL, NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8301, 'g', 'fieldman3', 'fieldman', NULL, NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8302, 'g', 'admin', 'admin', NULL, NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8303, 'g', 'supervisor', 'supervisor', NULL, NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8304, 'g', 'fieldman1', 'fieldman', NULL, NULL, NULL, NULL);
INSERT INTO public.casbin_rule VALUES (8305, 'g', 'harrypotter', 'admin', NULL, NULL, NULL, NULL);


--
-- TOC entry 3656 (class 0 OID 26916)
-- Dependencies: 227
-- Data for Name: departments; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.departments VALUES (1, 'IT', 'IT', 'Information Technology', true, 1, '2026-02-02 07:18:52.790641+00', NULL);
INSERT INTO public.departments VALUES (2, 'Marketing', 'MKT', 'Marketing and Communications', true, 2, '2026-02-02 07:18:52.790641+00', NULL);
INSERT INTO public.departments VALUES (3, 'Finance', 'FIN', 'Finance and Accounting', true, 3, '2026-02-02 07:18:52.790641+00', NULL);
INSERT INTO public.departments VALUES (4, 'HR', 'HR', 'Human Resources', true, 4, '2026-02-02 07:18:52.790641+00', NULL);
INSERT INTO public.departments VALUES (5, 'Operations', 'OPS', 'Business Operations', true, 5, '2026-02-02 07:18:52.790641+00', NULL);
INSERT INTO public.departments VALUES (6, 'Engineering', 'ENG', 'Engineering and Development', true, 6, '2026-02-02 07:18:52.790641+00', NULL);
INSERT INTO public.departments VALUES (7, 'Sales', 'SLS', 'Sales and Business Development', true, 7, '2026-02-02 07:18:52.790641+00', NULL);
INSERT INTO public.departments VALUES (8, 'Legal', 'LGL', 'Legal and Compliance', true, 8, '2026-02-02 07:18:52.790641+00', NULL);
INSERT INTO public.departments VALUES (9, 'Customer Support', 'CS', 'Customer Service and Support', true, 9, '2026-02-02 07:18:52.790641+00', NULL);


--
-- TOC entry 3652 (class 0 OID 26891)
-- Dependencies: 223
-- Data for Name: enum_definitions; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.enum_definitions VALUES (1, 'marital_status', 'Marital Status', 'Common marital status options', 'static', '[{"value": "single", "label": "Single"}, {"value": "married", "label": "Married"}, {"value": "divorced", "label": "Divorced"}, {"value": "widowed", "label": "Widowed"}, {"value": "separated", "label": "Separated"}]', NULL, NULL, NULL, 'null', NULL, 'GET', 'null', NULL, NULL, true, '2026-02-02 07:18:52.635236+00', NULL, 'system');
INSERT INTO public.enum_definitions VALUES (2, 'gender', 'Gender', 'Gender options', 'static', '[{"value": "male", "label": "Male"}, {"value": "female", "label": "Female"}, {"value": "other", "label": "Other"}, {"value": "prefer_not_to_say", "label": "Prefer not to say"}]', NULL, NULL, NULL, 'null', NULL, 'GET', 'null', NULL, NULL, true, '2026-02-02 07:18:52.646553+00', NULL, 'system');
INSERT INTO public.enum_definitions VALUES (3, 'employment_status', 'Employment Status', 'Employment status options', 'static', '[{"value": "employed", "label": "Employed"}, {"value": "self_employed", "label": "Self-Employed"}, {"value": "unemployed", "label": "Unemployed"}, {"value": "student", "label": "Student"}, {"value": "retired", "label": "Retired"}]', NULL, NULL, NULL, 'null', NULL, 'GET', 'null', NULL, NULL, true, '2026-02-02 07:18:52.654958+00', NULL, 'system');
INSERT INTO public.enum_definitions VALUES (4, 'education_level', 'Education Level', 'Educational attainment options', 'static', '[{"value": "elementary", "label": "Elementary"}, {"value": "high_school", "label": "High School"}, {"value": "vocational", "label": "Vocational"}, {"value": "college", "label": "College/University"}, {"value": "graduate", "label": "Graduate Degree"}]', NULL, NULL, NULL, 'null', NULL, 'GET', 'null', NULL, NULL, true, '2026-02-02 07:18:52.662572+00', NULL, 'system');
INSERT INTO public.enum_definitions VALUES (5, 'relationship_type', 'Relationship', 'Family relationship types', 'static', '[{"value": "spouse", "label": "Spouse"}, {"value": "child", "label": "Child"}, {"value": "parent", "label": "Parent"}, {"value": "sibling", "label": "Sibling"}, {"value": "other", "label": "Other"}]', NULL, NULL, NULL, 'null', NULL, 'GET', 'null', NULL, NULL, true, '2026-02-02 07:18:52.669629+00', NULL, 'system');
INSERT INTO public.enum_definitions VALUES (6, 'loan_purpose', 'Loan Purpose', 'Common loan purposes', 'static', '[{"value": "business", "label": "Business"}, {"value": "education", "label": "Education"}, {"value": "medical", "label": "Medical"}, {"value": "home_improvement", "label": "Home Improvement"}, {"value": "debt_consolidation", "label": "Debt Consolidation"}, {"value": "personal", "label": "Personal"}]', NULL, NULL, NULL, 'null', NULL, 'GET', 'null', NULL, NULL, true, '2026-02-02 07:18:52.679038+00', NULL, 'system');
INSERT INTO public.enum_definitions VALUES (7, 'yes_no', 'Yes/No', 'Simple yes/no options', 'static', '[{"value": "yes", "label": "Yes"}, {"value": "no", "label": "No"}]', NULL, NULL, NULL, 'null', NULL, 'GET', 'null', NULL, NULL, true, '2026-02-02 07:18:52.687994+00', NULL, 'system');
INSERT INTO public.enum_definitions VALUES (8, 'ph_regions', 'Philippine Regions', 'Philippine regions', 'static', '[{"value": "ncr", "label": "National Capital Region (NCR)"}, {"value": "car", "label": "Cordillera Administrative Region (CAR)"}, {"value": "region1", "label": "Region I (Ilocos Region)"}, {"value": "region2", "label": "Region II (Cagayan Valley)"}, {"value": "region3", "label": "Region III (Central Luzon)"}, {"value": "region4a", "label": "Region IV-A (CALABARZON)"}, {"value": "region4b", "label": "Region IV-B (MIMAROPA)"}, {"value": "region5", "label": "Region V (Bicol Region)"}, {"value": "region6", "label": "Region VI (Western Visayas)"}, {"value": "region7", "label": "Region VII (Central Visayas)"}, {"value": "region8", "label": "Region VIII (Eastern Visayas)"}, {"value": "region9", "label": "Region IX (Zamboanga Peninsula)"}, {"value": "region10", "label": "Region X (Northern Mindanao)"}, {"value": "region11", "label": "Region XI (Davao Region)"}, {"value": "region12", "label": "Region XII (SOCCSKSARGEN)"}, {"value": "region13", "label": "Region XIII (Caraga)"}, {"value": "barmm", "label": "BARMM (Bangsamoro)"}]', NULL, NULL, NULL, 'null', NULL, 'GET', 'null', NULL, NULL, true, '2026-02-02 07:18:52.696155+00', NULL, 'system');


--
-- TOC entry 3654 (class 0 OID 26903)
-- Dependencies: 225
-- Data for Name: field_type_definitions; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.field_type_definitions VALUES (1, 'text', 'Text Field', 'Single-line text input', 'string', '{"type": "string", "maxLength": 255}', '{"type": "string", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}', true, 'text', NULL, NULL, true, '2026-02-02 07:18:52.485587+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (2, 'long_text', 'Long Text / Textarea', 'Multi-line text input', 'string', '{"type": "string", "maxLength": 5000}', '{"type": "string", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}', true, 'textarea', NULL, NULL, true, '2026-02-02 07:18:52.501008+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (3, 'email', 'Email', 'Email address with validation', 'string', '{"type": "string", "format": "email", "maxLength": 255}', '{"type": "string", "format": "email", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}', true, 'email', NULL, NULL, true, '2026-02-02 07:18:52.509341+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (4, 'phone', 'Phone Number', 'Phone number (string format)', 'string', '{"type": "string", "pattern": "^[+]?[(]?[0-9]{1,4}[)]?[-\\s\\.]?[(]?[0-9]{1,4}[)]?[-\\s\\.]?[0-9]{1,9}$", "maxLength": 20}', '{"type": "string", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}', true, 'tel', NULL, NULL, true, '2026-02-02 07:18:52.51621+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (5, 'password', 'Password', 'Password input (hidden)', 'string', '{"type": "string", "minLength": 8, "maxLength": 100}', '{"type": "string", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}', true, 'password', NULL, NULL, true, '2026-02-02 07:18:52.524826+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (6, 'number', 'Number Field (Generic)', 'Any numeric value (int or float)', 'number', '{"type": "number"}', '{"type": "number", "not": {"type": ["string", "boolean", "array", "object"]}}', true, 'number', NULL, NULL, true, '2026-02-02 07:18:52.533044+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (7, 'integer', 'Integer Field', 'Whole numbers only (no decimals)', 'integer', '{"type": "integer"}', '{"type": "integer", "not": {"type": ["string", "boolean", "array", "object"]}}', true, 'number', NULL, NULL, true, '2026-02-02 07:18:52.540177+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (8, 'currency', 'Currency', 'Monetary value', 'number', '{"type": "number", "minimum": 0, "multipleOf": 0.01}', '{"type": "number", "not": {"type": ["string", "boolean", "array", "object"]}}', true, 'currency', '{"currency": "PHP", "locale": "en-PH"}', NULL, true, '2026-02-02 07:18:52.548665+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (9, 'percentage', 'Percentage', 'Percentage value (0-100)', 'number', '{"type": "number", "minimum": 0, "maximum": 100}', '{"type": "number", "not": {"type": ["string", "boolean", "array", "object"]}}', true, 'percentage', NULL, NULL, true, '2026-02-02 07:18:52.560498+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (10, 'date', 'Date Field', 'Date selector (YYYY-MM-DD)', 'string', '{"type": "string", "format": "date"}', '{"type": "string", "format": "date", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}', true, 'date', NULL, NULL, true, '2026-02-02 07:18:52.567149+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (11, 'boolean', 'Boolean / Checkbox', 'True/False value', 'boolean', '{"type": "boolean"}', '{"type": "boolean", "not": {"type": ["string", "number", "integer", "array", "object"]}}', true, 'checkbox', NULL, NULL, true, '2026-02-02 07:18:52.57361+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (12, 'enum', 'Enum Field / Dropdown', 'Select from predefined options', 'string', '{"type": "string", "enum": []}', '{"type": "string", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}', true, 'select', NULL, NULL, true, '2026-02-02 07:18:52.580651+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (13, 'file', 'File Upload', 'File upload field (returns token/URL)', 'string', '{"type": "string", "format": "uri"}', '{"type": "string", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}', true, 'file', NULL, NULL, true, '2026-02-02 07:18:52.58698+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (14, 'rating', 'Rating', 'Star rating or numeric score', 'integer', '{"type": "integer", "minimum": 1, "maximum": 5}', '{"type": "integer", "not": {"type": ["string", "boolean", "array", "object"]}}', true, 'rating', NULL, NULL, true, '2026-02-02 07:18:52.595208+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (15, 'url', 'URL Field', 'Web address with validation', 'string', '{"type": "string", "format": "uri", "maxLength": 500}', '{"type": "string", "format": "uri", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}', true, 'url', NULL, NULL, true, '2026-02-02 07:18:52.604811+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (16, 'json', 'JSON Field', 'Arbitrary JSON data', 'object', '{"type": "object"}', '{"type": "object", "not": {"type": ["string", "number", "integer", "boolean", "array"]}}', true, 'json', NULL, NULL, true, '2026-02-02 07:18:52.612789+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (17, 'address', 'Address (Structured)', 'Philippine address with structured fields', 'object', '{"type": "object", "properties": {"street": {"type": "string", "maxLength": 255}, "barangay": {"type": "string", "maxLength": 100}, "city": {"type": "string", "maxLength": 100}, "province": {"type": "string", "maxLength": 100}, "zip_code": {"type": "string", "pattern": "^[0-9]{4}$"}}, "required": ["city", "province"]}', '{"type": "object", "not": {"type": ["string", "number", "integer", "boolean", "array"]}, "properties": {"street": {"type": "string", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}, "barangay": {"type": "string", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}, "city": {"type": "string", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}, "province": {"type": "string", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}, "zip_code": {"type": "string", "not": {"type": ["number", "integer", "boolean", "array", "object"]}}}}', true, 'address', '{"country": "Philippines"}', NULL, true, '2026-02-02 07:18:52.620977+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (18, 'ph_mobile_number', 'Philippine Mobile Number', 'Philippine mobile number with +63 prefix', 'phone', '{"type": "string", "pattern": "^\\+639\\d{9}$", "description": "Format: +639XXXXXXXXX"}', '{"pattern": "^\\+639\\d{9}$"}', true, 'tel', 'null', 'null', true, '2026-02-02 07:18:52.703658+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (19, 'ph_tin', 'Philippine TIN', 'Philippine Tax Identification Number', 'text', '{"type": "string", "pattern": "^\\d{3}-\\d{3}-\\d{3}-\\d{3}$", "description": "Format: XXX-XXX-XXX-XXX"}', '{"pattern": "^\\d{3}-\\d{3}-\\d{3}-\\d{3}$"}', true, 'text', 'null', 'null', true, '2026-02-02 07:18:52.710429+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (20, 'ph_sss_number', 'Philippine SSS Number', 'Philippine Social Security System number', 'text', '{"type": "string", "pattern": "^\\d{2}-\\d{7}-\\d{1}$", "description": "Format: XX-XXXXXXX-X"}', '{"pattern": "^\\d{2}-\\d{7}-\\d{1}$"}', true, 'text', 'null', 'null', true, '2026-02-02 07:18:52.71604+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (21, 'credit_card_number', 'Credit Card Number', 'Credit card number (16 digits)', 'text', '{"type": "string", "pattern": "^\\d{16}$", "minLength": 16, "maxLength": 16}', '{"pattern": "^\\d{16}$"}', true, 'text', '{"inputType": "password", "mask": "####-####-####-####"}', 'null', true, '2026-02-02 07:18:52.721122+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (22, 'full_name', 'Full Name', 'Complete name with proper validation', 'text', '{"type": "string", "minLength": 2, "maxLength": 100, "pattern": "^[a-zA-Z\\s\\-\\.]+$"}', '{"minLength": 2, "maxLength": 100, "pattern": "^[a-zA-Z\\s\\-\\.]+$"}', true, 'text', 'null', 'null', true, '2026-02-02 07:18:52.726603+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (23, 'adult_age', 'Adult Age', 'Age for adults only (18-100)', 'integer', '{"type": "integer", "minimum": 18, "maximum": 100}', '{"minimum": 18, "maximum": 100}', true, 'updown', 'null', 'null', true, '2026-02-02 07:18:52.733058+00', NULL, 'system');
INSERT INTO public.field_type_definitions VALUES (24, 'monthly_salary', 'Monthly Salary (PHP)', 'Monthly salary in Philippine Peso', 'currency', '{"type": "number", "minimum": 0, "maximum": 10000000, "multipleOf": 0.01}', '{"minimum": 0, "maximum": 10000000}', true, 'currency', '{"currency": "PHP", "locale": "en-PH"}', 'null', true, '2026-02-02 07:18:52.740152+00', NULL, 'system');


--
-- TOC entry 3677 (class 0 OID 27152)
-- Dependencies: 248
-- Data for Name: file_uploads; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.file_uploads VALUES (1, 'c905f90b-6d48-4383-a426-1649f421ac3b', 'samplefile.pdf', 'file_530f77c9_1770192789914_samplefile.pdf', 'application/pdf', 1377202, 1, 'field_1770167284559', '2026-02-04 08:13:09.896931+00', 'fieldman1');


--
-- TOC entry 3672 (class 0 OID 27075)
-- Dependencies: 243
-- Data for Name: form_field_mappings; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3670 (class 0 OID 27038)
-- Dependencies: 241
-- Data for Name: form_submissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.form_submissions VALUES (1, 13, 'fieldman1', 4, 'submitted', '{"field_1770017215469": "", "field_1770167284559": "c905f90b-6d48-4383-a426-1649f421ac3b"}', '["c905f90b-6d48-4383-a426-1649f421ac3b"]', '[]', true, NULL, NULL, NULL, NULL, NULL, '2026-02-04 08:13:09.90768+00', '2026-02-04 08:13:09.896931+00', '2026-02-04 08:13:09.896931+00');
INSERT INTO public.form_submissions VALUES (2, 13, 'fieldman1', 4, 'draft', '{"field_1770017215469": "", "field_1770167284559": null}', '[]', '[{"field": "field_1770167284559", "message": "None is not of type ''string''", "constraint": "type"}]', false, NULL, NULL, NULL, NULL, NULL, NULL, '2026-02-04 08:13:28.536997+00', NULL);


--
-- TOC entry 3662 (class 0 OID 26964)
-- Dependencies: 233
-- Data for Name: form_templates; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.form_templates VALUES (12, 1, 'BDO Loan Application Form', '1.1', NULL, '{"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "title": "Form", "properties": {"field_1770016947597": {"title": "Text Input", "type": "string"}, "field_1770106069052": {"title": "Text Input", "type": "string"}}, "required": []}', '[{"id": "field_1770016947597", "type": "text", "label": "Text Input", "required": false, "placeholder": "", "options": null, "validation": {}, "show_if": null}, {"id": "field_1770106069052", "type": "text", "label": "Text Input", "required": false, "placeholder": "", "options": null, "validation": {}, "show_if": null}]', 'null', 'Form template created with 2 fields', true, '2026-02-02 07:22:33.648871+00', '2026-02-04 06:33:30.837503+00', NULL);
INSERT INTO public.form_templates VALUES (28, 1, 'BDO Loan Application Form', '1.1', NULL, '{"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "title": "Form", "properties": {"field_1770172771678": {"title": "Text Input", "type": "string"}}, "required": []}', '[{"id": "field_1770172771678", "type": "text", "label": "Text Input", "required": false, "placeholder": "", "options": null, "validation": {}, "show_if": null}]', 'null', 'Form template created with 1 fields', true, '2026-02-04 02:39:34.084219+00', '2026-02-04 07:13:32.375003+00', NULL);
INSERT INTO public.form_templates VALUES (13, 2, 'Auto Loan Application', '1.0', NULL, '{"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "title": "Form", "properties": {"field_1770017215469": {"title": "Text Input", "type": "string"}, "field_1770167284559": {"title": "File Upload", "type": "string"}}, "required": []}', '[{"id": "field_1770017215469", "type": "text", "label": "Text Input", "required": false, "placeholder": "", "options": null, "validation": {}, "show_if": null}, {"id": "field_1770167284559", "type": "file", "label": "File Upload", "required": false, "placeholder": "", "options": null, "validation": {}, "show_if": null}]', 'null', 'Form template created with 2 fields', true, '2026-02-02 07:26:59.92817+00', '2026-02-04 01:08:06.519973+00', NULL);
INSERT INTO public.form_templates VALUES (29, 3, 'Personal Loan Application', '1.0', NULL, '{"$schema": "http://json-schema.org/draft-07/schema#", "type": "object", "title": "Form", "properties": {"field_1770172784851": {"title": "Text Input", "type": "string"}}, "required": []}', '[{"id": "field_1770172784851", "type": "text", "label": "Text Input", "required": false, "placeholder": "", "options": null, "validation": {}, "show_if": null}]', 'null', 'Form template created with 1 fields', true, '2026-02-04 02:39:47.238211+00', NULL, NULL);


--
-- TOC entry 3658 (class 0 OID 26928)
-- Dependencies: 229
-- Data for Name: locations; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.locations VALUES (1, 'Makati', 'MKT', 'Makati City', 'Metro Manila', true, 1, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (2, 'Quezon City', 'QC', 'Quezon City', 'Metro Manila', true, 2, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (3, 'Paranaque', 'PNQ', 'Paranaque City', 'Metro Manila', true, 3, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (4, 'Pampanga', 'PAM', 'Pampanga Province', 'Central Luzon', true, 4, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (5, 'Bulacan', 'BUL', 'Bulacan Province', 'Central Luzon', true, 5, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (6, 'Cavite', 'CAV', 'Cavite Province', 'CALABARZON', true, 6, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (7, 'Laguna', 'LAG', 'Laguna Province', 'CALABARZON', true, 7, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (8, 'Batangas', 'BAT', 'Batangas Province', 'CALABARZON', true, 8, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (9, 'Cebu', 'CEB', 'Cebu City', 'Central Visayas', true, 9, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (10, 'Iloilo', 'ILO', 'Iloilo City', 'Western Visayas', true, 10, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (11, 'Bacolod', 'BAC', 'Bacolod City', 'Western Visayas', true, 11, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (12, 'Davao', 'DVO', 'Davao City', 'Davao Region', true, 12, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (13, 'Cagayan De Oro', 'CDO', 'Cagayan De Oro City', 'Northern Mindanao', true, 13, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (14, 'Pagadian', 'PAG', 'Pagadian City', 'Zamboanga Peninsula', true, 14, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (15, 'Tagum', 'TAG', 'Tagum City', 'Davao Region', true, 15, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (16, 'Zamboanga', 'ZAM', 'Zamboanga City', 'Zamboanga Peninsula', true, 16, '2026-02-02 07:18:52.817277+00', NULL);
INSERT INTO public.locations VALUES (17, 'General Santos', 'GNS', 'General Santos City', 'SOCCSKSARGEN', true, 17, '2026-02-02 07:18:52.817277+00', NULL);


--
-- TOC entry 3666 (class 0 OID 27004)
-- Dependencies: 237
-- Data for Name: refresh_tokens; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.refresh_tokens VALUES (1, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDYyMTY3OSwidHlwZSI6InJlZnJlc2gifQ.lTbJJZT8JnGLM5eSsgtWE989KqtWaBBTmCt5T-TUw90', '2026-02-09 07:21:19.392272+00', false, '2026-02-02 07:21:19.124334+00');
INSERT INTO public.refresh_tokens VALUES (2, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDYyMTg2NywidHlwZSI6InJlZnJlc2gifQ.mzOkPcNDYEDr6j48M8ZXSnLNvl-xkTtQa1c5dIIIEHA', '2026-02-09 07:24:27.332137+00', false, '2026-02-02 07:24:26.992783+00');
INSERT INTO public.refresh_tokens VALUES (3, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDYyMjc3NywidHlwZSI6InJlZnJlc2gifQ.uqZr546aNhvGAAyCiOoWE2tpXbCIvkF3RSNjbzj3FYM', '2026-02-09 07:39:37.992766+00', false, '2026-02-02 07:39:37.645919+00');
INSERT INTO public.refresh_tokens VALUES (4, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDY4MTQwMywidHlwZSI6InJlZnJlc2gifQ.i3cJIccoRKibN4EsL8s5Js3OAum8if1gNiDZz1JlFMc', '2026-02-09 23:56:43.140065+00', false, '2026-02-02 23:56:42.708886+00');
INSERT INTO public.refresh_tokens VALUES (5, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDY4MjMxNCwidHlwZSI6InJlZnJlc2gifQ.kRacUUQ_zQlKv-UELNJPBk43-pInpQ7eZBw5kVRVIHk', '2026-02-10 00:11:54.406872+00', false, '2026-02-03 00:11:53.984358+00');
INSERT INTO public.refresh_tokens VALUES (6, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDY4MzAwMiwidHlwZSI6InJlZnJlc2gifQ.hdwTBT44z2tiqbq8dJj8FuVUZ2X6dfl-ealLaQMHv4o', '2026-02-10 00:23:22.623405+00', false, '2026-02-03 00:23:22.199305+00');
INSERT INTO public.refresh_tokens VALUES (7, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDY4NDU4MSwidHlwZSI6InJlZnJlc2gifQ.fsA7b9wre8wH_wMz7p5JKs22Ii-mHPRRcyEx1EL5Jgk', '2026-02-10 00:49:41.237309+00', false, '2026-02-03 00:49:40.85721+00');
INSERT INTO public.refresh_tokens VALUES (8, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDY4NTk5OSwidHlwZSI6InJlZnJlc2gifQ.G8YHrC7-CUUWbAbJLGihXuknsX4_VWgnOeM2vXMJEOg', '2026-02-10 01:13:19.719936+00', false, '2026-02-03 01:13:19.256858+00');
INSERT INTO public.refresh_tokens VALUES (9, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDY4NjEwNiwidHlwZSI6InJlZnJlc2gifQ.dKQ0rSkjZzDxwblU0oQk7UAZsronYW_YWtvOyi4MDoc', '2026-02-10 01:15:06.654468+00', false, '2026-02-03 01:15:06.271319+00');
INSERT INTO public.refresh_tokens VALUES (10, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDY4NjM0NCwidHlwZSI6InJlZnJlc2gifQ._bbUFt0qSUPlktpXlJS2QldzQtUqWZji-lhlLcmNAgM', '2026-02-10 01:19:04.880189+00', false, '2026-02-03 01:19:04.434038+00');
INSERT INTO public.refresh_tokens VALUES (11, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDY4NjQyOCwidHlwZSI6InJlZnJlc2gifQ.NZulh8xkJn_8UooS-WSI040qRmRH5Emd3lGzxg_z52g', '2026-02-10 01:20:28.767962+00', false, '2026-02-03 01:20:28.382369+00');
INSERT INTO public.refresh_tokens VALUES (12, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDY4NjQ0NywidHlwZSI6InJlZnJlc2gifQ.6gpv7XMvod6rZ5C4Jjx-ldJXpQiIu9GVwSvTM-gzAbg', '2026-02-10 01:20:47.949278+00', false, '2026-02-03 01:20:47.552693+00');
INSERT INTO public.refresh_tokens VALUES (13, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDY4ODM4MiwidHlwZSI6InJlZnJlc2gifQ.7Fbxf3D4WqKSVGqop3eZBW7qCK_qtd6NYPHvYuAzt0U', '2026-02-10 01:53:02.806529+00', false, '2026-02-03 01:53:02.369102+00');
INSERT INTO public.refresh_tokens VALUES (14, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwMDcxNCwidHlwZSI6InJlZnJlc2gifQ.76XxOINHgwQVeGnsxqEs1kn0u6t_35PzZEDgAN11hLI', '2026-02-10 05:18:34.961743+00', false, '2026-02-03 05:18:30.741668+00');
INSERT INTO public.refresh_tokens VALUES (15, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwMDcxNywidHlwZSI6InJlZnJlc2gifQ.WHxFerXhloWDsrxA83D30b7BCSQKQIBbUDYs9mgh6NI', '2026-02-10 05:18:37.457933+00', false, '2026-02-03 05:18:33.699493+00');
INSERT INTO public.refresh_tokens VALUES (16, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwMDcxOSwidHlwZSI6InJlZnJlc2gifQ.RQnVY1dGiWlxHsG8ZexjLQ8ixoAGGEBDmmTF3wSx5Tw', '2026-02-10 05:18:39.803662+00', false, '2026-02-03 05:18:35.768737+00');
INSERT INTO public.refresh_tokens VALUES (17, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwMTIxNiwidHlwZSI6InJlZnJlc2gifQ.qNQQCQWWvFwPF9lVSwBscLPtukAdtPoUgFKn4D_QTfQ', '2026-02-10 05:26:56.568698+00', false, '2026-02-03 05:26:56.039574+00');
INSERT INTO public.refresh_tokens VALUES (18, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwMTk5NiwidHlwZSI6InJlZnJlc2gifQ.bCVkLwAeGOQPbLTn34wlTiic3hW9G7wZbhyRvWVIbcQ', '2026-02-10 05:39:56.254263+00', false, '2026-02-03 05:39:55.842631+00');
INSERT INTO public.refresh_tokens VALUES (19, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwMzY5MCwidHlwZSI6InJlZnJlc2gifQ.Yfmhha71MV7b7GO6QSeK6MFwPA2h_CQuL1n19BOCFK4', '2026-02-10 06:08:10.859031+00', false, '2026-02-03 06:08:10.45456+00');
INSERT INTO public.refresh_tokens VALUES (20, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwNTA3NiwidHlwZSI6InJlZnJlc2gifQ.DsI2fji2h_-bf0NUgaz9Z4RCwrarEmnS56X5oZJaXBI', '2026-02-10 06:31:16.473989+00', false, '2026-02-03 06:31:16.088794+00');
INSERT INTO public.refresh_tokens VALUES (21, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwNjI3NCwidHlwZSI6InJlZnJlc2gifQ.MpxinkUSzhQIAXrWYw1B2Y9jF8SI1fxB0X_5kt_mGc8', '2026-02-10 06:51:14.193825+00', false, '2026-02-03 06:51:13.777127+00');
INSERT INTO public.refresh_tokens VALUES (22, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwNjMzMywidHlwZSI6InJlZnJlc2gifQ.ShvYPkmggV3j51NdyqboVZrmjcdSQBFRmFk4s1icvgQ', '2026-02-10 06:52:13.106028+00', false, '2026-02-03 06:52:12.645934+00');
INSERT INTO public.refresh_tokens VALUES (23, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwNjM1MiwidHlwZSI6InJlZnJlc2gifQ.EDJUJqAmR9kugD-On1Bdh-hkV2nfkHvgkt9L8U2RWEA', '2026-02-10 06:52:32.185024+00', false, '2026-02-03 06:52:31.808348+00');
INSERT INTO public.refresh_tokens VALUES (24, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwNjQyMywidHlwZSI6InJlZnJlc2gifQ.RoCICAMXVYNVQZJGMfSJ9isuSY_fMJ0rEEPqcmbJjrg', '2026-02-10 06:53:43.641444+00', false, '2026-02-03 06:53:43.219713+00');
INSERT INTO public.refresh_tokens VALUES (25, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwNjQzMywidHlwZSI6InJlZnJlc2gifQ.9UOkIyrxY4eGyIH63aCEtH-dd2-COlFX-G--hM0dtMY', '2026-02-10 06:53:53.764768+00', false, '2026-02-03 06:53:53.385513+00');
INSERT INTO public.refresh_tokens VALUES (26, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwNjUzMiwidHlwZSI6InJlZnJlc2gifQ.yTomtIdk2J3sBOXJk6AXU5YSOEQ8CDGc0fG_PFylGVk', '2026-02-10 06:55:32.206193+00', false, '2026-02-03 06:55:31.829767+00');
INSERT INTO public.refresh_tokens VALUES (27, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwNjUzOSwidHlwZSI6InJlZnJlc2gifQ.k3IsK9xzChn1Gg2cZ9NgXq4rfA38ccx7bWz97odc35s', '2026-02-10 06:55:39.082099+00', false, '2026-02-03 06:55:38.654375+00');
INSERT INTO public.refresh_tokens VALUES (28, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwNjg0OSwidHlwZSI6InJlZnJlc2gifQ.c4gtJanU3U5DrSpP2L9rmuE1gGbMYXQUWRabP_PNqHo', '2026-02-10 07:00:49.442967+00', false, '2026-02-03 07:00:49.077666+00');
INSERT INTO public.refresh_tokens VALUES (29, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwNzg0NywidHlwZSI6InJlZnJlc2gifQ.W7_3YbffYTwSRxVdGWtT9o4bCqUb5sgeN8BEhp8Rn0s', '2026-02-10 07:17:27.362271+00', false, '2026-02-03 07:17:26.971679+00');
INSERT INTO public.refresh_tokens VALUES (30, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwNzkzOSwidHlwZSI6InJlZnJlc2gifQ.bTH8LPy2hciygTPXsNUNyGwknsTzTYswX7AMBYl9q18', '2026-02-10 07:18:59.697222+00', false, '2026-02-03 07:18:59.289932+00');
INSERT INTO public.refresh_tokens VALUES (31, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwNzk3NiwidHlwZSI6InJlZnJlc2gifQ.E4aqFWmORvPinPULZ_MBM95MHIc6fUT45AHDlVlUwcY', '2026-02-10 07:19:36.554026+00', false, '2026-02-03 07:19:36.058796+00');
INSERT INTO public.refresh_tokens VALUES (32, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwODg4NiwidHlwZSI6InJlZnJlc2gifQ.VYemFWsKroHuGkH_KN-dJ4lDyytApnmp5rn0vzhQC2U', '2026-02-10 07:34:46.445036+00', false, '2026-02-03 07:34:45.96548+00');
INSERT INTO public.refresh_tokens VALUES (33, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcwOTc5NSwidHlwZSI6InJlZnJlc2gifQ.h-p8lJXB1enUxhh6_XGF-2scGebcvIIhRHr1UvJdV5Q', '2026-02-10 07:49:55.897751+00', false, '2026-02-03 07:49:55.389216+00');
INSERT INTO public.refresh_tokens VALUES (34, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcxMDcwOSwidHlwZSI6InJlZnJlc2gifQ.MlS5Zyw5aM3tn_vSqqt4PNFU1UEH-f_bbMzu7BvlyWU', '2026-02-10 08:05:09.908085+00', false, '2026-02-03 08:05:09.369799+00');
INSERT INTO public.refresh_tokens VALUES (35, 4, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaWVsZG1hbjEiLCJleHAiOjE3NzA3MTE0NzQsInR5cGUiOiJyZWZyZXNoIn0.rebIWbXN97t8RPtxj1WXbwC5eUHvG3MVMmD-FApg9SY', '2026-02-10 08:17:54.029915+00', false, '2026-02-03 08:17:53.618415+00');
INSERT INTO public.refresh_tokens VALUES (36, 4, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaWVsZG1hbjEiLCJleHAiOjE3NzA3MTE0ODUsInR5cGUiOiJyZWZyZXNoIn0.kCaYCnUOl14mCzYvHWMMk46hKU6tXKT2KpHWRrRhBqA', '2026-02-10 08:18:05.202612+00', false, '2026-02-03 08:18:04.851389+00');
INSERT INTO public.refresh_tokens VALUES (37, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcxMTUyNywidHlwZSI6InJlZnJlc2gifQ.m9i2u0eEqMKfGVdcb-tUnkccRIrIWX5FvnVzif_0Lac', '2026-02-10 08:18:47.056522+00', false, '2026-02-03 08:18:46.666079+00');
INSERT INTO public.refresh_tokens VALUES (38, 4, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaWVsZG1hbjEiLCJleHAiOjE3NzA3MTE1MzgsInR5cGUiOiJyZWZyZXNoIn0.vHtwcJnh0CjySHpAhb_dcVCTVP-21eqCvhqIEjiVLdY', '2026-02-10 08:18:58.296139+00', false, '2026-02-03 08:18:57.88738+00');
INSERT INTO public.refresh_tokens VALUES (39, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDcxMTYyNiwidHlwZSI6InJlZnJlc2gifQ.AnIWHynZ0OrD3N-CBCs0iBMPvYWfXLO1zaD_M3-hiU8', '2026-02-10 08:20:26.781011+00', false, '2026-02-03 08:20:26.393745+00');
INSERT INTO public.refresh_tokens VALUES (40, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc2Njc2OSwidHlwZSI6InJlZnJlc2gifQ.gZvuz_0tTO7-nVxb9JZtWx29Zk5wywZ3MXEEXPQwvns', '2026-02-10 23:39:29.193167+00', false, '2026-02-03 23:39:28.518049+00');
INSERT INTO public.refresh_tokens VALUES (41, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc2NzE5NiwidHlwZSI6InJlZnJlc2gifQ.3E6lpmxtkmMkAXqg90pgboTn2ee3KS_yPeUoN1ZnM8I', '2026-02-10 23:46:36.726102+00', false, '2026-02-03 23:46:36.09399+00');
INSERT INTO public.refresh_tokens VALUES (42, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc2ODAwMCwidHlwZSI6InJlZnJlc2gifQ.Sbmf-q6GBekmZmMWFa2ohYwqvsYjIQncXYCSBxBMV7U', '2026-02-11 00:00:00.200954+00', false, '2026-02-03 23:59:59.649937+00');
INSERT INTO public.refresh_tokens VALUES (43, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc2ODk2NCwidHlwZSI6InJlZnJlc2gifQ.qNQHKl2VRTLKTu_VSI8lJ4UtDZcl33SXe4MlAlCJOgs', '2026-02-11 00:16:04.947139+00', false, '2026-02-04 00:16:02.689285+00');
INSERT INTO public.refresh_tokens VALUES (44, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3MDM1MSwidHlwZSI6InJlZnJlc2gifQ.qJ4FLNICOZj_iahWBVJs0n-qqhSInhdpywMIVRcKuTc', '2026-02-11 00:39:11.077573+00', false, '2026-02-04 00:39:10.64484+00');
INSERT INTO public.refresh_tokens VALUES (45, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3MTgxNywidHlwZSI6InJlZnJlc2gifQ.aJPyLMuWkNgRMzUCQU47voeNTlhxn0PKDmC1apHRFZ0', '2026-02-11 01:03:37.767962+00', false, '2026-02-04 01:03:37.364719+00');
INSERT INTO public.refresh_tokens VALUES (46, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3MjA3NiwidHlwZSI6InJlZnJlc2gifQ.TbX5s2QjhOCq2-FN8JyGL7JU1K4TxiLwf2jXLjh2s-Y', '2026-02-11 01:07:56.364058+00', false, '2026-02-04 01:07:55.943672+00');
INSERT INTO public.refresh_tokens VALUES (47, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3MzE1MiwidHlwZSI6InJlZnJlc2gifQ.m-OxDuPpiUtZQ6Hv67E-kOQk5fSTSzJoKggL3B1K9b0', '2026-02-11 01:25:52.73954+00', false, '2026-02-04 01:25:52.123295+00');
INSERT INTO public.refresh_tokens VALUES (48, 3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdXBlcnZpc29yIiwiZXhwIjoxNzcwNzczMTY4LCJ0eXBlIjoicmVmcmVzaCJ9.K_tdHDR77iukFW2vLcy1M3I-0YNx0zwhWXS3apShOCE', '2026-02-11 01:26:08.02987+00', false, '2026-02-04 01:26:07.688592+00');
INSERT INTO public.refresh_tokens VALUES (49, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3MzE4MiwidHlwZSI6InJlZnJlc2gifQ.NFKq3xD2WdZa_0qnPCFTZieK-gqVtc6As4v-JBTJjR8', '2026-02-11 01:26:22.789033+00', false, '2026-02-04 01:26:22.400746+00');
INSERT INTO public.refresh_tokens VALUES (50, 3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdXBlcnZpc29yIiwiZXhwIjoxNzcwNzczMTk2LCJ0eXBlIjoicmVmcmVzaCJ9.NM6xqm1zYcOTvMBCna9Txnuk0RP8Cun1v6FCHMr-Eac', '2026-02-11 01:26:36.972763+00', false, '2026-02-04 01:26:36.554242+00');
INSERT INTO public.refresh_tokens VALUES (51, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3MzIzOCwidHlwZSI6InJlZnJlc2gifQ.F8IqktgGG2jhSJnd9gSyD_w4Nk9pPXOvABDEaw8VRd4', '2026-02-11 01:27:18.11542+00', false, '2026-02-04 01:27:17.651382+00');
INSERT INTO public.refresh_tokens VALUES (52, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3NDI3MywidHlwZSI6InJlZnJlc2gifQ.dzToCuHf56VllbTHjyFcBRbm8LGc1TQsEi11PolPN4U', '2026-02-11 01:44:33.735855+00', false, '2026-02-04 01:44:33.308734+00');
INSERT INTO public.refresh_tokens VALUES (53, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3NTY0NCwidHlwZSI6InJlZnJlc2gifQ.3aKY_hmavR4gvzvIr8QHcze7P3zrjKLKSCY5lWiB4FA', '2026-02-11 02:07:24.989266+00', false, '2026-02-04 02:07:24.468338+00');
INSERT INTO public.refresh_tokens VALUES (54, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3NjY0NSwidHlwZSI6InJlZnJlc2gifQ.7soGSIay8cKyLMlgry0iwTfYrhBh7rqQDd_GxVDudgE', '2026-02-11 02:24:05.573127+00', false, '2026-02-04 02:24:05.068348+00');
INSERT INTO public.refresh_tokens VALUES (55, 3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdXBlcnZpc29yIiwiZXhwIjoxNzcwNzc2NzA3LCJ0eXBlIjoicmVmcmVzaCJ9.wXf82ncIN3JoskPImPvCWDQ-_f_t24IFq1FKXsENyAw', '2026-02-11 02:25:07.667378+00', false, '2026-02-04 02:25:07.255354+00');
INSERT INTO public.refresh_tokens VALUES (56, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3NjcyNSwidHlwZSI6InJlZnJlc2gifQ.lIuUXN3E9aXbqGTlic8npZA0cbrZ08xtNuZaDb0rqTw', '2026-02-11 02:25:25.789816+00', false, '2026-02-04 02:25:25.451674+00');
INSERT INTO public.refresh_tokens VALUES (57, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3Njc1NywidHlwZSI6InJlZnJlc2gifQ.pn1_OvbHmhxxtJ-00sVIxCPdlqgHxrfko2Su9XBoNSw', '2026-02-11 02:25:57.409273+00', false, '2026-02-04 02:25:57.042006+00');
INSERT INTO public.refresh_tokens VALUES (58, 3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdXBlcnZpc29yIiwiZXhwIjoxNzcwNzc2NzcyLCJ0eXBlIjoicmVmcmVzaCJ9.dDfO5GF8wY6vKW2smXeNreqUxvNQQPMQBCbzfEVYCv4', '2026-02-11 02:26:12.386982+00', false, '2026-02-04 02:26:12.01475+00');
INSERT INTO public.refresh_tokens VALUES (59, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3Njc4MSwidHlwZSI6InJlZnJlc2gifQ.il1ICEux4dqnm9oaEMZtm6zsBnsGpSX9hhhYBYb0yL0', '2026-02-11 02:26:21.429193+00', false, '2026-02-04 02:26:21.024281+00');
INSERT INTO public.refresh_tokens VALUES (60, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3NzgwNywidHlwZSI6InJlZnJlc2gifQ.Ohx3wAwcY00hhgSACF9FkepC4Hnp-ptb72zNVmwavA4', '2026-02-11 02:43:27.524352+00', false, '2026-02-04 02:43:26.988739+00');
INSERT INTO public.refresh_tokens VALUES (61, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc3OTczNSwidHlwZSI6InJlZnJlc2gifQ.WI1fMaZbpGBmsplvXyCK2MAY8Jh7twtFVmAeLBRzRTQ', '2026-02-11 03:15:35.383131+00', false, '2026-02-04 03:15:34.87977+00');
INSERT INTO public.refresh_tokens VALUES (62, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc4MTI2MywidHlwZSI6InJlZnJlc2gifQ.twx82i4SATCkZV1nFVdBppBrc7jxElTkGmG8-_DL6-E', '2026-02-11 03:41:03.607997+00', false, '2026-02-04 03:41:01.220532+00');
INSERT INTO public.refresh_tokens VALUES (63, 3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdXBlcnZpc29yIiwiZXhwIjoxNzcwNzgxMzgyLCJ0eXBlIjoicmVmcmVzaCJ9.tP7rI2Xeg8F-PoNzR4wQFP8vuzlJ1M68bYWnPbYPr-A', '2026-02-11 03:43:02.261015+00', false, '2026-02-04 03:43:00.512388+00');
INSERT INTO public.refresh_tokens VALUES (64, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc4MTQwNCwidHlwZSI6InJlZnJlc2gifQ.x6ws2dlgoow0lwGciENhZAlR-6F02Nskni1SSdnDqEQ', '2026-02-11 03:43:24.046382+00', false, '2026-02-04 03:43:22.097842+00');
INSERT INTO public.refresh_tokens VALUES (65, 3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdXBlcnZpc29yIiwiZXhwIjoxNzcwNzgxNDY3LCJ0eXBlIjoicmVmcmVzaCJ9.qeqtcGMjOW-ugTqBE6pIvaJgfFImnrMV-ZnTrE2h2AM', '2026-02-11 03:44:27.026551+00', false, '2026-02-04 03:44:25.469594+00');
INSERT INTO public.refresh_tokens VALUES (66, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc4MTYwMiwidHlwZSI6InJlZnJlc2gifQ.6rL2HpwmF8AP8lWrKngJRIkmlM11OoKLQnqmd9sVbIg', '2026-02-11 03:46:42.377141+00', false, '2026-02-04 03:46:40.579644+00');
INSERT INTO public.refresh_tokens VALUES (67, 3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdXBlcnZpc29yIiwiZXhwIjoxNzcwNzgxNjMxLCJ0eXBlIjoicmVmcmVzaCJ9.Fh_oO204qKm4jRqqVCAfpEeRK-meroonupa5F3l3Ru8', '2026-02-11 03:47:11.469367+00', false, '2026-02-04 03:47:08.928656+00');
INSERT INTO public.refresh_tokens VALUES (68, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc4MTY1NywidHlwZSI6InJlZnJlc2gifQ.J3U3cF_tbJP5WF9SdezSUltJGJlu76aHqIQYEPGUx9o', '2026-02-11 03:47:37.869728+00', false, '2026-02-04 03:47:35.877922+00');
INSERT INTO public.refresh_tokens VALUES (69, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc4NjUxMSwidHlwZSI6InJlZnJlc2gifQ.9OA7gZK-dAg26cVsrCsitbbehi5JykJBrz0ueTe3QQ0', '2026-02-11 05:08:31.84706+00', false, '2026-02-04 05:08:27.130737+00');
INSERT INTO public.refresh_tokens VALUES (70, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc4NzQ3NywidHlwZSI6InJlZnJlc2gifQ.TwZCdgyo1vtGx4EKMxJolqJls-EObl-ZS0xlylv0nJU', '2026-02-11 05:24:37.9856+00', false, '2026-02-04 05:24:37.580069+00');
INSERT INTO public.refresh_tokens VALUES (71, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc4ODcyMSwidHlwZSI6InJlZnJlc2gifQ.w-lpsPIh2e_OVGf_7fZfR3xoYqy69VAP0hlRLPuoJqo', '2026-02-11 05:45:21.052581+00', false, '2026-02-04 05:45:20.557746+00');
INSERT INTO public.refresh_tokens VALUES (72, 2, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc3MDc4OTU2OSwidHlwZSI6InJlZnJlc2gifQ.OPtw-fqTJz4mGXt_KmiN7vVsYut5J4Ww4J-FT-tlkzw', '2026-02-11 05:59:29.188996+00', false, '2026-02-04 05:59:28.888759+00');
INSERT INTO public.refresh_tokens VALUES (73, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc4OTU5MywidHlwZSI6InJlZnJlc2gifQ.xzwz8JkMMN7t_2jeEJ0Q_yNdDnQ_9rJRjC6Langp5aw', '2026-02-11 05:59:53.100687+00', false, '2026-02-04 05:59:52.734325+00');
INSERT INTO public.refresh_tokens VALUES (74, 2, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc3MDc4OTYxMywidHlwZSI6InJlZnJlc2gifQ.MJKEIRsZ5W2fFwDgTcawqPT8FhopmqZzThfw1nrmkek', '2026-02-11 06:00:13.475002+00', false, '2026-02-04 06:00:13.120496+00');
INSERT INTO public.refresh_tokens VALUES (75, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc4OTY0MiwidHlwZSI6InJlZnJlc2gifQ.F9ip7VubPZN4sX6PTLWBrWXd3l4aLCTLPNaLMkPQvyU', '2026-02-11 06:00:42.404881+00', false, '2026-02-04 06:00:42.07989+00');
INSERT INTO public.refresh_tokens VALUES (76, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc5MTQ4NywidHlwZSI6InJlZnJlc2gifQ.hAA0Jms7ImE-olb3i6nstKetobQo9p2DDfbegFHkemg', '2026-02-11 06:31:27.040901+00', false, '2026-02-04 06:31:26.633761+00');
INSERT INTO public.refresh_tokens VALUES (77, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc5MTQ4OCwidHlwZSI6InJlZnJlc2gifQ.SrvwZzbWKwQELHjmmWzSNnv__CZde4BZpUN2QXLlnYE', '2026-02-11 06:31:28.203509+00', false, '2026-02-04 06:31:27.346431+00');
INSERT INTO public.refresh_tokens VALUES (78, 2, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc3MDc5MTY2OCwidHlwZSI6InJlZnJlc2gifQ.-2h77ZCwBQvW08EBsWN7AKclRSzYW0BkNbi-DkTSns8', '2026-02-11 06:34:28.367296+00', false, '2026-02-04 06:34:27.914298+00');
INSERT INTO public.refresh_tokens VALUES (79, 2, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc3MDc5MTY4MywidHlwZSI6InJlZnJlc2gifQ.ekj1LooxXGIARAPjHIrCaVeyCyTgqR-PoBwVrJQ_vMw', '2026-02-11 06:34:43.925676+00', false, '2026-02-04 06:34:43.531921+00');
INSERT INTO public.refresh_tokens VALUES (80, 3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdXBlcnZpc29yIiwiZXhwIjoxNzcwNzkxNjk5LCJ0eXBlIjoicmVmcmVzaCJ9.uS7Na7QFBMHB2U5z5Jygoypm9PlqN5lD81oGyoCCpVo', '2026-02-11 06:34:59.034883+00', false, '2026-02-04 06:34:58.575153+00');
INSERT INTO public.refresh_tokens VALUES (81, 2, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc3MDc5MTcyMywidHlwZSI6InJlZnJlc2gifQ.lzcaNobYitB5NhDV23WlF2elQuzGq1THeRxiqbcibnM', '2026-02-11 06:35:23.187388+00', false, '2026-02-04 06:35:22.80507+00');
INSERT INTO public.refresh_tokens VALUES (82, 3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdXBlcnZpc29yIiwiZXhwIjoxNzcwNzkxNzUyLCJ0eXBlIjoicmVmcmVzaCJ9.NZq13ai55KgOJ_veqYd-bQ_xUmAY0qPQl-qX67ru4Xw', '2026-02-11 06:35:52.44308+00', false, '2026-02-04 06:35:52.072707+00');
INSERT INTO public.refresh_tokens VALUES (83, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc5MTc3MSwidHlwZSI6InJlZnJlc2gifQ.q7uv43zbR72wYlcU4ReC3aFOdcVSFP-LxG7LS7ruEFA', '2026-02-11 06:36:11.777944+00', false, '2026-02-04 06:36:11.384486+00');
INSERT INTO public.refresh_tokens VALUES (84, 2, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc3MDc5MTc4NCwidHlwZSI6InJlZnJlc2gifQ.BQn-aS3mbeVJ5joeg_LL49gDY78NlpAs-pXAGXE3alw', '2026-02-11 06:36:24.359255+00', false, '2026-02-04 06:36:23.924032+00');
INSERT INTO public.refresh_tokens VALUES (85, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc5MTgxMywidHlwZSI6InJlZnJlc2gifQ.158XkeL_4tWA3eeMnDseNcjrcW5fiN545GsxT84-17g', '2026-02-11 06:36:53.771835+00', false, '2026-02-04 06:36:53.347108+00');
INSERT INTO public.refresh_tokens VALUES (86, 2, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsImV4cCI6MTc3MDc5MTg2OCwidHlwZSI6InJlZnJlc2gifQ.ZpLXUvIIZ0KTy5KosRuQS-FbcouQyFa2IAAyJdV-0eE', '2026-02-11 06:37:48.266026+00', false, '2026-02-04 06:37:47.849854+00');
INSERT INTO public.refresh_tokens VALUES (87, 3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdXBlcnZpc29yIiwiZXhwIjoxNzcwNzkxODgwLCJ0eXBlIjoicmVmcmVzaCJ9.QdhXLqDIqnGuzuXa530Ri14fycCSOH7Leh-rjNdioL0', '2026-02-11 06:38:00.736631+00', false, '2026-02-04 06:38:00.306291+00');
INSERT INTO public.refresh_tokens VALUES (88, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc5MTkxNCwidHlwZSI6InJlZnJlc2gifQ.W8uf3qFDxK39G3SQeFda1jX497LcOEfJnowp0xndL9M', '2026-02-11 06:38:34.847093+00', false, '2026-02-04 06:38:34.454453+00');
INSERT INTO public.refresh_tokens VALUES (89, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc5MjQyMSwidHlwZSI6InJlZnJlc2gifQ.8B6mFLMtry9s0Cu8rdEy_U5u7-6fwKpzMQzgseUDoIA', '2026-02-11 06:47:01.709785+00', false, '2026-02-04 06:47:01.314989+00');
INSERT INTO public.refresh_tokens VALUES (90, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc5MzkyMCwidHlwZSI6InJlZnJlc2gifQ.lT-ijDNj5l0gq7_iky-_QyPhU_o-gbsaCoCZGRYNB_s', '2026-02-11 07:12:00.32275+00', false, '2026-02-04 07:11:59.644085+00');
INSERT INTO public.refresh_tokens VALUES (91, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc5NDExMSwidHlwZSI6InJlZnJlc2gifQ.iAt6Xrp5JI8e79ukr4VOXu01xZ8Eamczjtx6VK9-9BQ', '2026-02-11 07:15:11.054755+00', false, '2026-02-04 07:15:10.679319+00');
INSERT INTO public.refresh_tokens VALUES (92, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc5NDkyMCwidHlwZSI6InJlZnJlc2gifQ.l9iIdKlXsZy26lx3569KuY3Gtj64QzEEOQXW5f2Hyxw', '2026-02-11 07:28:40.396253+00', false, '2026-02-04 07:28:39.984271+00');
INSERT INTO public.refresh_tokens VALUES (93, 3, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzdXBlcnZpc29yIiwiZXhwIjoxNzcwNzk1NDk4LCJ0eXBlIjoicmVmcmVzaCJ9.lkprG6R-kvJh4wMda5IZUOl41_wvgEyZS9wcMRU-jkY', '2026-02-11 07:38:18.576884+00', false, '2026-02-04 07:38:18.165745+00');
INSERT INTO public.refresh_tokens VALUES (94, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc5NTUxMSwidHlwZSI6InJlZnJlc2gifQ.t1iiHgAfZnNAzKAL5eLgqvoxb13-JGWexSa0nhheETk', '2026-02-11 07:38:31.432161+00', false, '2026-02-04 07:38:31.041786+00');
INSERT INTO public.refresh_tokens VALUES (95, 4, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaWVsZG1hbjEiLCJleHAiOjE3NzA3OTcyNTMsInR5cGUiOiJyZWZyZXNoIn0.dEZttDybeKlgdVTiiPec0Ax_OMUPiYUYMfb7bnflDNs', '2026-02-11 08:07:33.906796+00', false, '2026-02-04 08:07:33.666281+00');
INSERT INTO public.refresh_tokens VALUES (96, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc5NzI4MCwidHlwZSI6InJlZnJlc2gifQ.pG6RUnkHv5WpTyGdSuLtsqGnUzXGPqd5gZN6-dP2Wps', '2026-02-11 08:08:00.915117+00', false, '2026-02-04 08:08:00.467203+00');
INSERT INTO public.refresh_tokens VALUES (97, 4, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaWVsZG1hbjEiLCJleHAiOjE3NzA3OTc1ODAsInR5cGUiOiJyZWZyZXNoIn0.fVqRXZoPmjrSKNwPyBmLkCNY6kcsz7UZeBC14fNFwNs', '2026-02-11 08:13:00.953717+00', false, '2026-02-04 08:13:00.592788+00');
INSERT INTO public.refresh_tokens VALUES (98, 5, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaWVsZG1hbjIiLCJleHAiOjE3NzA3OTc2MjIsInR5cGUiOiJyZWZyZXNoIn0.YMSQqgCKqoVDm9YYkarptolKsS6TdKOObPaidFJTl5c', '2026-02-11 08:13:42.845487+00', false, '2026-02-04 08:13:42.589517+00');
INSERT INTO public.refresh_tokens VALUES (99, 4, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJmaWVsZG1hbjEiLCJleHAiOjE3NzA3OTc3NTcsInR5cGUiOiJyZWZyZXNoIn0.ybyQNapgwNHdqBOD15nlLLdeYzAyaCbBhLM7tG_Iaoc', '2026-02-11 08:15:57.322365+00', false, '2026-02-04 08:15:56.908782+00');
INSERT INTO public.refresh_tokens VALUES (100, 1, 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJoYXJyeXBvdHRlciIsImV4cCI6MTc3MDc5NzgwMywidHlwZSI6InJlZnJlc2gifQ.ybgxhxFWy7azuCnyeefBhFy0pVlFmQr7_LanGgViFjk', '2026-02-11 08:16:43.797654+00', false, '2026-02-04 08:16:43.392025+00');


--
-- TOC entry 3646 (class 0 OID 26855)
-- Dependencies: 217
-- Data for Name: resource_attributes; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3644 (class 0 OID 26844)
-- Dependencies: 215
-- Data for Name: resource_relationships; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3664 (class 0 OID 26982)
-- Dependencies: 235
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.roles VALUES (2, 'supervisor', 'Review and approve submissions for their bank', '["forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review"]', '2026-02-02 07:49:05.88743+00', 1, '2026-02-04 07:38:13.389065+00', 1);
INSERT INTO public.roles VALUES (3, 'fieldman', 'Submit forms and manage own submissions', '["users:read", "roles:read", "forms:read", "templates:read", "submissions:create", "submissions:read", "submissions:update"]', '2026-02-02 07:50:01.041905+00', 1, '2026-02-03 08:18:52.780766+00', 1);
INSERT INTO public.roles VALUES (1, 'admin', 'Administrator', '["users:create", "users:read", "users:update", "users:delete", "roles:create", "roles:read", "roles:update", "roles:delete", "forms:create", "forms:read", "forms:update", "forms:delete", "templates:create", "templates:read", "templates:update", "templates:delete", "submissions:create", "submissions:read", "submissions:viewDetails", "submissions:update", "submissions:delete", "submissions:review", "banks:create", "banks:read", "banks:update", "banks:delete", "policies:create", "policies:read", "policies:update", "policies:delete", "system:configure"]', '2026-02-02 07:20:24.175792+00', NULL, '2026-02-04 06:38:44.048269+00', 1);


--
-- TOC entry 3668 (class 0 OID 27022)
-- Dependencies: 239
-- Data for Name: user_attributes; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 3675 (class 0 OID 27136)
-- Dependencies: 246
-- Data for Name: user_roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.user_roles VALUES (4, 3);
INSERT INTO public.user_roles VALUES (2, 1);
INSERT INTO public.user_roles VALUES (6, 3);
INSERT INTO public.user_roles VALUES (5, 3);
INSERT INTO public.user_roles VALUES (3, 2);
INSERT INTO public.user_roles VALUES (1, 1);


--
-- TOC entry 3660 (class 0 OID 26940)
-- Dependencies: 231
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.users VALUES (1, 'harrypotter', 'harrypotter@example.com', '$2b$12$zC.HaSyhwcpb0cf94ifY3.HR6C7zZwNI8YpT8s.gu1fo2BrbMWGiu', 'admin', NULL, true, true, 'Harry', 'Potter', 'Harry Potter', 'Legal', 3, 'Makati', '2026-02-02 07:20:24.175792+00', '2026-02-04 06:34:14.102537+00', 1);
INSERT INTO public.users VALUES (3, 'supervisor', 'supervisor@example.com', '$2b$12$jDg289xtNo24OIlrbRKi3ecRTd.Lg/MqhxfLetv.GY7Z14DxTA3o6', 'supervisor', NULL, true, false, 'Jane', 'Doe', 'Jane Doe', 'Customer Support', 2, 'Paranaque', '2026-02-03 00:00:09.962869+00', '2026-02-04 06:34:50.288717+00', 2);
INSERT INTO public.users VALUES (5, 'fieldman2', 'fieldman2@example.com', '$2b$12$1rOgqvoXUjLDZUCDSncIQuk37u3G0dRgxeEIGB18sm8hAmQXc7aBa', 'fieldman', NULL, true, false, 'John', 'Doe', 'John Doe', 'Customer Support', 1, 'Bacolod', '2026-02-03 00:01:04.856124+00', '2026-02-03 07:25:20.217272+00', 1);
INSERT INTO public.users VALUES (2, 'admin', 'admin@example.com', '$2b$12$pvGZXiMLcUzfAJXYJBdBsuaF5KEcIY1lpawS2x6JR87EApo5i0qwK', 'admin', NULL, true, false, 'John', 'Doe', 'John Doe', 'Legal', 1, 'Quezon City', '2026-02-02 07:50:36.536601+00', '2026-02-03 08:14:27.195567+00', 1);
INSERT INTO public.users VALUES (4, 'fieldman1', 'fieldman1@example.com', '$2b$12$eZS6L/HpSdgyAXGSSzTnQOvPXHDJR7TTVMtBpXcPp0HQdZuSrwZDq', 'fieldman', NULL, true, false, 'John', 'Doe', 'John  Doe', 'Customer Support', 1, 'Tagum', '2026-02-03 00:00:43.106727+00', '2026-02-03 08:19:15.046848+00', 1);
INSERT INTO public.users VALUES (6, 'fieldman3', 'fieldman3@example.com', '$2b$12$OmF1gTWwwGC0FGTJ9nYrfOKfoofRMqzga.J8grN/Rg176u1PH/kHa', 'fieldman', NULL, true, false, 'John', 'Doe', 'John Doe', 'Operations', 1, 'Tagum', '2026-02-03 00:01:29.341319+00', '2026-02-04 00:58:22.39243+00', 1);


--
-- TOC entry 3721 (class 0 OID 0)
-- Dependencies: 218
-- Name: abac_policies_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.abac_policies_id_seq', 6, true);


--
-- TOC entry 3722 (class 0 OID 0)
-- Dependencies: 244
-- Name: audit_logs_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.audit_logs_id_seq', 225, true);


--
-- TOC entry 3723 (class 0 OID 0)
-- Dependencies: 220
-- Name: banks_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.banks_id_seq', 5, true);


--
-- TOC entry 3724 (class 0 OID 0)
-- Dependencies: 249
-- Name: casbin_rule_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.casbin_rule_id_seq', 8305, true);


--
-- TOC entry 3725 (class 0 OID 0)
-- Dependencies: 226
-- Name: departments_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.departments_id_seq', 9, true);


--
-- TOC entry 3726 (class 0 OID 0)
-- Dependencies: 222
-- Name: enum_definitions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.enum_definitions_id_seq', 8, true);


--
-- TOC entry 3727 (class 0 OID 0)
-- Dependencies: 224
-- Name: field_type_definitions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.field_type_definitions_id_seq', 24, true);


--
-- TOC entry 3728 (class 0 OID 0)
-- Dependencies: 247
-- Name: file_uploads_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.file_uploads_id_seq', 1, true);


--
-- TOC entry 3729 (class 0 OID 0)
-- Dependencies: 242
-- Name: form_field_mappings_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.form_field_mappings_id_seq', 1, false);


--
-- TOC entry 3730 (class 0 OID 0)
-- Dependencies: 240
-- Name: form_submissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.form_submissions_id_seq', 2, true);


--
-- TOC entry 3731 (class 0 OID 0)
-- Dependencies: 232
-- Name: form_templates_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.form_templates_id_seq', 30, false);


--
-- TOC entry 3732 (class 0 OID 0)
-- Dependencies: 228
-- Name: locations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.locations_id_seq', 17, true);


--
-- TOC entry 3733 (class 0 OID 0)
-- Dependencies: 236
-- Name: refresh_tokens_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.refresh_tokens_id_seq', 100, true);


--
-- TOC entry 3734 (class 0 OID 0)
-- Dependencies: 216
-- Name: resource_attributes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.resource_attributes_id_seq', 1, false);


--
-- TOC entry 3735 (class 0 OID 0)
-- Dependencies: 214
-- Name: resource_relationships_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.resource_relationships_id_seq', 1, false);


--
-- TOC entry 3736 (class 0 OID 0)
-- Dependencies: 234
-- Name: roles_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_id_seq', 3, true);


--
-- TOC entry 3737 (class 0 OID 0)
-- Dependencies: 238
-- Name: user_attributes_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.user_attributes_id_seq', 1, false);


--
-- TOC entry 3738 (class 0 OID 0)
-- Dependencies: 230
-- Name: users_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_id_seq', 6, true);


--
-- TOC entry 3392 (class 2606 OID 26874)
-- Name: abac_policies abac_policies_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.abac_policies
    ADD CONSTRAINT abac_policies_pkey PRIMARY KEY (id);


--
-- TOC entry 3458 (class 2606 OID 27109)
-- Name: audit_logs audit_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_pkey PRIMARY KEY (id);


--
-- TOC entry 3396 (class 2606 OID 26886)
-- Name: banks banks_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.banks
    ADD CONSTRAINT banks_pkey PRIMARY KEY (id);


--
-- TOC entry 3479 (class 2606 OID 27188)
-- Name: casbin_rule casbin_rule_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.casbin_rule
    ADD CONSTRAINT casbin_rule_pkey PRIMARY KEY (id);


--
-- TOC entry 3409 (class 2606 OID 26924)
-- Name: departments departments_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_code_key UNIQUE (code);


--
-- TOC entry 3411 (class 2606 OID 26922)
-- Name: departments departments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.departments
    ADD CONSTRAINT departments_pkey PRIMARY KEY (id);


--
-- TOC entry 3401 (class 2606 OID 26899)
-- Name: enum_definitions enum_definitions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.enum_definitions
    ADD CONSTRAINT enum_definitions_pkey PRIMARY KEY (id);


--
-- TOC entry 3405 (class 2606 OID 26912)
-- Name: field_type_definitions field_type_definitions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.field_type_definitions
    ADD CONSTRAINT field_type_definitions_pkey PRIMARY KEY (id);


--
-- TOC entry 3472 (class 2606 OID 27160)
-- Name: file_uploads file_uploads_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_uploads
    ADD CONSTRAINT file_uploads_pkey PRIMARY KEY (id);


--
-- TOC entry 3474 (class 2606 OID 27162)
-- Name: file_uploads file_uploads_storage_path_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_uploads
    ADD CONSTRAINT file_uploads_storage_path_key UNIQUE (storage_path);


--
-- TOC entry 3452 (class 2606 OID 27080)
-- Name: form_field_mappings form_field_mappings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_field_mappings
    ADD CONSTRAINT form_field_mappings_pkey PRIMARY KEY (id);


--
-- TOC entry 3443 (class 2606 OID 27046)
-- Name: form_submissions form_submissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_submissions
    ADD CONSTRAINT form_submissions_pkey PRIMARY KEY (id);


--
-- TOC entry 3426 (class 2606 OID 26972)
-- Name: form_templates form_templates_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_templates
    ADD CONSTRAINT form_templates_pkey PRIMARY KEY (id);


--
-- TOC entry 3417 (class 2606 OID 26936)
-- Name: locations locations_code_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_code_key UNIQUE (code);


--
-- TOC entry 3419 (class 2606 OID 26934)
-- Name: locations locations_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.locations
    ADD CONSTRAINT locations_pkey PRIMARY KEY (id);


--
-- TOC entry 3438 (class 2606 OID 27012)
-- Name: refresh_tokens refresh_tokens_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_pkey PRIMARY KEY (id);


--
-- TOC entry 3390 (class 2606 OID 26863)
-- Name: resource_attributes resource_attributes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resource_attributes
    ADD CONSTRAINT resource_attributes_pkey PRIMARY KEY (id);


--
-- TOC entry 3387 (class 2606 OID 26852)
-- Name: resource_relationships resource_relationships_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.resource_relationships
    ADD CONSTRAINT resource_relationships_pkey PRIMARY KEY (id);


--
-- TOC entry 3433 (class 2606 OID 26990)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (id);


--
-- TOC entry 3456 (class 2606 OID 27082)
-- Name: form_field_mappings uq_template_field; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_field_mappings
    ADD CONSTRAINT uq_template_field UNIQUE (template_id, field_name);


--
-- TOC entry 3441 (class 2606 OID 27030)
-- Name: user_attributes user_attributes_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_attributes
    ADD CONSTRAINT user_attributes_pkey PRIMARY KEY (id);


--
-- TOC entry 3470 (class 2606 OID 27140)
-- Name: user_roles user_roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_pkey PRIMARY KEY (user_id, role_id);


--
-- TOC entry 3424 (class 2606 OID 26949)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (id);


--
-- TOC entry 3393 (class 1259 OID 26876)
-- Name: ix_abac_policies_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_abac_policies_id ON public.abac_policies USING btree (id);


--
-- TOC entry 3394 (class 1259 OID 26875)
-- Name: ix_abac_policies_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_abac_policies_name ON public.abac_policies USING btree (name);


--
-- TOC entry 3459 (class 1259 OID 27135)
-- Name: ix_audit_logs_action; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_action ON public.audit_logs USING btree (action);


--
-- TOC entry 3460 (class 1259 OID 34257)
-- Name: ix_audit_logs_created_at; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_created_at ON public.audit_logs USING btree (created_at);


--
-- TOC entry 3461 (class 1259 OID 34256)
-- Name: ix_audit_logs_entity_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_entity_id ON public.audit_logs USING btree (entity_id);


--
-- TOC entry 3462 (class 1259 OID 34255)
-- Name: ix_audit_logs_entity_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_entity_name ON public.audit_logs USING btree (entity_name);


--
-- TOC entry 3463 (class 1259 OID 27132)
-- Name: ix_audit_logs_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_id ON public.audit_logs USING btree (id);


--
-- TOC entry 3464 (class 1259 OID 34254)
-- Name: ix_audit_logs_page; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_page ON public.audit_logs USING btree (page);


--
-- TOC entry 3465 (class 1259 OID 27131)
-- Name: ix_audit_logs_resource_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_resource_id ON public.audit_logs USING btree (resource_id);


--
-- TOC entry 3466 (class 1259 OID 27130)
-- Name: ix_audit_logs_resource_type; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_resource_type ON public.audit_logs USING btree (resource_type);


--
-- TOC entry 3467 (class 1259 OID 27134)
-- Name: ix_audit_logs_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_user_id ON public.audit_logs USING btree (user_id);


--
-- TOC entry 3468 (class 1259 OID 27133)
-- Name: ix_audit_logs_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_audit_logs_username ON public.audit_logs USING btree (username);


--
-- TOC entry 3397 (class 1259 OID 26887)
-- Name: ix_banks_code; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_banks_code ON public.banks USING btree (code);


--
-- TOC entry 3398 (class 1259 OID 26889)
-- Name: ix_banks_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_banks_id ON public.banks USING btree (id);


--
-- TOC entry 3399 (class 1259 OID 26888)
-- Name: ix_banks_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_banks_name ON public.banks USING btree (name);


--
-- TOC entry 3412 (class 1259 OID 26925)
-- Name: ix_departments_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_departments_id ON public.departments USING btree (id);


--
-- TOC entry 3413 (class 1259 OID 26926)
-- Name: ix_departments_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_departments_name ON public.departments USING btree (name);


--
-- TOC entry 3402 (class 1259 OID 26901)
-- Name: ix_enum_definitions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_enum_definitions_id ON public.enum_definitions USING btree (id);


--
-- TOC entry 3403 (class 1259 OID 26900)
-- Name: ix_enum_definitions_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_enum_definitions_name ON public.enum_definitions USING btree (name);


--
-- TOC entry 3406 (class 1259 OID 26914)
-- Name: ix_field_type_definitions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_field_type_definitions_id ON public.field_type_definitions USING btree (id);


--
-- TOC entry 3407 (class 1259 OID 26913)
-- Name: ix_field_type_definitions_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_field_type_definitions_name ON public.field_type_definitions USING btree (name);


--
-- TOC entry 3475 (class 1259 OID 27168)
-- Name: ix_file_uploads_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_file_uploads_id ON public.file_uploads USING btree (id);


--
-- TOC entry 3476 (class 1259 OID 27169)
-- Name: ix_file_uploads_submission_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_file_uploads_submission_id ON public.file_uploads USING btree (submission_id);


--
-- TOC entry 3477 (class 1259 OID 27170)
-- Name: ix_file_uploads_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_file_uploads_token ON public.file_uploads USING btree (token);


--
-- TOC entry 3453 (class 1259 OID 27098)
-- Name: ix_form_field_mappings_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_field_mappings_id ON public.form_field_mappings USING btree (id);


--
-- TOC entry 3454 (class 1259 OID 27099)
-- Name: ix_form_field_mappings_template_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_field_mappings_template_id ON public.form_field_mappings USING btree (template_id);


--
-- TOC entry 3444 (class 1259 OID 27070)
-- Name: ix_form_submissions_fieldman_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_submissions_fieldman_id ON public.form_submissions USING btree (fieldman_id);


--
-- TOC entry 3445 (class 1259 OID 27071)
-- Name: ix_form_submissions_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_submissions_id ON public.form_submissions USING btree (id);


--
-- TOC entry 3446 (class 1259 OID 27069)
-- Name: ix_form_submissions_status; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_submissions_status ON public.form_submissions USING btree (status);


--
-- TOC entry 3447 (class 1259 OID 27073)
-- Name: ix_form_submissions_submitted_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_submissions_submitted_by ON public.form_submissions USING btree (submitted_by);


--
-- TOC entry 3448 (class 1259 OID 27068)
-- Name: ix_form_submissions_template_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_submissions_template_id ON public.form_submissions USING btree (template_id);


--
-- TOC entry 3449 (class 1259 OID 27067)
-- Name: ix_form_submissions_validated_by; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_submissions_validated_by ON public.form_submissions USING btree (validated_by);


--
-- TOC entry 3450 (class 1259 OID 27072)
-- Name: ix_form_submissions_validated_on; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_submissions_validated_on ON public.form_submissions USING btree (validated_on);


--
-- TOC entry 3427 (class 1259 OID 26978)
-- Name: ix_form_templates_bank_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_templates_bank_id ON public.form_templates USING btree (bank_id);


--
-- TOC entry 3428 (class 1259 OID 26979)
-- Name: ix_form_templates_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_templates_id ON public.form_templates USING btree (id);


--
-- TOC entry 3429 (class 1259 OID 26980)
-- Name: ix_form_templates_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_form_templates_name ON public.form_templates USING btree (name);


--
-- TOC entry 3414 (class 1259 OID 26938)
-- Name: ix_locations_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_locations_id ON public.locations USING btree (id);


--
-- TOC entry 3415 (class 1259 OID 26937)
-- Name: ix_locations_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_locations_name ON public.locations USING btree (name);


--
-- TOC entry 3434 (class 1259 OID 27019)
-- Name: ix_refresh_tokens_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_refresh_tokens_id ON public.refresh_tokens USING btree (id);


--
-- TOC entry 3435 (class 1259 OID 27018)
-- Name: ix_refresh_tokens_token; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_refresh_tokens_token ON public.refresh_tokens USING btree (token);


--
-- TOC entry 3436 (class 1259 OID 27020)
-- Name: ix_refresh_tokens_user_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_refresh_tokens_user_id ON public.refresh_tokens USING btree (user_id);


--
-- TOC entry 3388 (class 1259 OID 26864)
-- Name: ix_resource_attributes_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resource_attributes_id ON public.resource_attributes USING btree (id);


--
-- TOC entry 3385 (class 1259 OID 26853)
-- Name: ix_resource_relationships_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_resource_relationships_id ON public.resource_relationships USING btree (id);


--
-- TOC entry 3430 (class 1259 OID 27002)
-- Name: ix_roles_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_roles_id ON public.roles USING btree (id);


--
-- TOC entry 3431 (class 1259 OID 27001)
-- Name: ix_roles_name; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_roles_name ON public.roles USING btree (name);


--
-- TOC entry 3439 (class 1259 OID 27036)
-- Name: ix_user_attributes_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_user_attributes_id ON public.user_attributes USING btree (id);


--
-- TOC entry 3420 (class 1259 OID 26961)
-- Name: ix_users_email; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_email ON public.users USING btree (email);


--
-- TOC entry 3421 (class 1259 OID 26962)
-- Name: ix_users_id; Type: INDEX; Schema: public; Owner: postgres
--

CREATE INDEX ix_users_id ON public.users USING btree (id);


--
-- TOC entry 3422 (class 1259 OID 26960)
-- Name: ix_users_username; Type: INDEX; Schema: public; Owner: postgres
--

CREATE UNIQUE INDEX ix_users_username ON public.users USING btree (username);


--
-- TOC entry 3494 (class 2606 OID 27115)
-- Name: audit_logs audit_logs_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id);


--
-- TOC entry 3495 (class 2606 OID 27125)
-- Name: audit_logs audit_logs_deleted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_deleted_by_fkey FOREIGN KEY (deleted_by) REFERENCES public.users(id);


--
-- TOC entry 3496 (class 2606 OID 27120)
-- Name: audit_logs audit_logs_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id);


--
-- TOC entry 3497 (class 2606 OID 27110)
-- Name: audit_logs audit_logs_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.audit_logs
    ADD CONSTRAINT audit_logs_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3500 (class 2606 OID 27163)
-- Name: file_uploads file_uploads_submission_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.file_uploads
    ADD CONSTRAINT file_uploads_submission_id_fkey FOREIGN KEY (submission_id) REFERENCES public.form_submissions(id);


--
-- TOC entry 3491 (class 2606 OID 27093)
-- Name: form_field_mappings form_field_mappings_enum_definition_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_field_mappings
    ADD CONSTRAINT form_field_mappings_enum_definition_id_fkey FOREIGN KEY (enum_definition_id) REFERENCES public.enum_definitions(id);


--
-- TOC entry 3492 (class 2606 OID 27088)
-- Name: form_field_mappings form_field_mappings_field_type_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_field_mappings
    ADD CONSTRAINT form_field_mappings_field_type_id_fkey FOREIGN KEY (field_type_id) REFERENCES public.field_type_definitions(id);


--
-- TOC entry 3493 (class 2606 OID 27083)
-- Name: form_field_mappings form_field_mappings_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_field_mappings
    ADD CONSTRAINT form_field_mappings_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.form_templates(id);


--
-- TOC entry 3487 (class 2606 OID 27057)
-- Name: form_submissions form_submissions_reviewed_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_submissions
    ADD CONSTRAINT form_submissions_reviewed_by_fkey FOREIGN KEY (reviewed_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 3488 (class 2606 OID 27052)
-- Name: form_submissions form_submissions_submitted_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_submissions
    ADD CONSTRAINT form_submissions_submitted_by_fkey FOREIGN KEY (submitted_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 3489 (class 2606 OID 27047)
-- Name: form_submissions form_submissions_template_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_submissions
    ADD CONSTRAINT form_submissions_template_id_fkey FOREIGN KEY (template_id) REFERENCES public.form_templates(id);


--
-- TOC entry 3490 (class 2606 OID 27062)
-- Name: form_submissions form_submissions_validated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_submissions
    ADD CONSTRAINT form_submissions_validated_by_fkey FOREIGN KEY (validated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 3482 (class 2606 OID 26973)
-- Name: form_templates form_templates_bank_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.form_templates
    ADD CONSTRAINT form_templates_bank_id_fkey FOREIGN KEY (bank_id) REFERENCES public.banks(id);


--
-- TOC entry 3485 (class 2606 OID 27013)
-- Name: refresh_tokens refresh_tokens_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.refresh_tokens
    ADD CONSTRAINT refresh_tokens_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3483 (class 2606 OID 26991)
-- Name: roles roles_created_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_created_by_fkey FOREIGN KEY (created_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 3484 (class 2606 OID 26996)
-- Name: roles roles_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 3486 (class 2606 OID 27031)
-- Name: user_attributes user_attributes_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_attributes
    ADD CONSTRAINT user_attributes_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id) ON DELETE CASCADE;


--
-- TOC entry 3498 (class 2606 OID 27146)
-- Name: user_roles user_roles_role_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_role_id_fkey FOREIGN KEY (role_id) REFERENCES public.roles(id);


--
-- TOC entry 3499 (class 2606 OID 27141)
-- Name: user_roles user_roles_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_roles
    ADD CONSTRAINT user_roles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id);


--
-- TOC entry 3480 (class 2606 OID 26950)
-- Name: users users_bank_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_bank_id_fkey FOREIGN KEY (bank_id) REFERENCES public.banks(id);


--
-- TOC entry 3481 (class 2606 OID 26955)
-- Name: users users_updated_by_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_updated_by_fkey FOREIGN KEY (updated_by) REFERENCES public.users(id) ON DELETE SET NULL;


--
-- TOC entry 3686 (class 0 OID 0)
-- Dependencies: 5
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE USAGE ON SCHEMA public FROM PUBLIC;


-- Completed on 2026-02-04 08:18:10 UTC

--
-- PostgreSQL database dump complete
--

\unrestrict Te6H1lx00Sx1xnPxBEKxNVYKBvkmxeCEucGWhcvxpG1CbFdHUxKAM1ibnxdw5io

