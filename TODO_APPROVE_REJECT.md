# Task: Add functional approve and reject buttons in application details in submissions page

## Plan:
1. Update `submissions.js` to show approve/reject buttons when:
   - Submission status is "submitted" or "validated"
   - User has review permission (admin, supervisor, or has 'review' action on 'submissions')
   
2. Enhance the viewSubmission modal with better UI for review actions

## Steps:
- [x] 1. Update viewSubmission() in submissions.js to show/hide approve/reject buttons based on status and permissions
- [x] 2. Enhance approveSubmission() with loading state and better feedback
- [x] 3. Enhance rejectSubmission() with modal prompt instead of browser prompt
- [x] 4. Implementation complete


