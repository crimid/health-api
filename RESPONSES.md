# Lab 7: HealthTrack API - Written Responses

**Name:** Jeff Muthomi
**Admission Number:** C027-01-0870/2024
**Date:** 25th July 2026

---

## Exercise 1: Authentication Logic

### Q1: Why is it important to store the JWT secret key in an environment variable instead of hardcoding it?

Storing the JWT secret key in an environment variable prevents it from being exposed in the codebase. If the code is pushed to a public repository like GitHub, the hardcoded secret would be visible to anyone, allowing attackers to forge valid JWT tokens and impersonate any user. Environment variables also allow different keys for development, testing, and production environments without changing code.

### Q2: What would happen if the JWT secret key is compromised?

If the JWT secret key is compromised, an attacker could create valid JWT tokens for any user, impersonate them, and access all protected resources. This would completely break the authentication system, compromise all user accounts, and potentially expose sensitive patient medical records. The only fix would be to rotate the secret key immediately, which would invalidate all existing tokens and force all users to log in again.

### Q3: Why do we use HttpOnly cookies for storing JWT tokens?

HttpOnly cookies prevent client-side JavaScript from accessing the token, protecting against Cross-Site Scripting (XSS) attacks. Even if an attacker injects malicious scripts into the page, they cannot steal the token because the browser won't allow JavaScript to read HttpOnly cookies. This adds an important layer of security against token theft.

---

## Exercise 2: Password Reset

### Q1: What security measures should be in place for password reset?

Reset tokens should have short expiration times (1 hour), be cryptographically random, and be stored securely in the database with expiry timestamps. Rate limiting should be implemented to prevent multiple requests from the same IP address. Users should receive email notifications when a reset is requested, and the system should never disclose whether an email address is registered (to prevent user enumeration attacks).

### Q2: How would you prevent abuse of the forgot password endpoint?

Implement rate limiting to restrict the number of reset requests per IP address per hour (e.g., 5 requests per hour). Use CAPTCHA verification for additional protection against automated attacks. Only send reset emails to registered email addresses and don't disclose whether the email exists in the system. Log all reset attempts and monitor for suspicious patterns.

### Q3: Why should reset tokens have an expiration time?

Expiration limits the window of opportunity for an attacker to use a stolen or intercepted reset token. Even if a token is compromised, it becomes useless after the expiration time (typically 1 hour), reducing the risk of account compromise. This follows the security principle of "least privilege" and ensures that tokens have a limited lifespan.

---

## Exercise 3: Role-Based Access Control

### Q1: Why is it important to have role-based access control in a medical application?

RBAC ensures patient privacy by restricting access to sensitive medical records based on the user's role. Patients can only see their own records, doctors can only see their assigned patients, and administrators have full access for system management. This complies with healthcare regulations like HIPAA and Kenya's Data Protection Act, ensuring that only authorized personnel can access patient data.

### Q2: How would you handle a scenario where a patient needs to be assigned to multiple doctors?

You would need to implement a many-to-many relationship between patients and doctors using a junction table (e.g., `patient_doctors`), instead of a single `doctor_id` field. This allows a patient to have multiple doctors, and each doctor can be assigned to multiple patients. The junction table would store `patient_id` and `doctor_id` pairs, along with additional metadata like assignment date and primary doctor flag.

### Q3: What happens if a user's role is changed (e.g., from "patient" to "doctor")?

The user's permissions would change immediately with their next authenticated request. If a patient is promoted to doctor, they would gain access to doctor-only endpoints but would need to be assigned patients. If a doctor is demoted to patient, they would lose access to doctor-only endpoints but retain access to their own patient records. The role change should be logged for audit purposes and may require reassignment of existing relationships.

---

## Exercise 4: Token Blacklisting

### Q1: Why is token blacklisting necessary when JWTs are stateless?

While JWTs are stateless by design, blacklisting allows immediate invalidation of tokens before they expire. This is essential for real-world scenarios like user logout, password changes, account suspension, or when a user's account is compromised. Without blacklisting, a stolen token would remain valid until its natural expiration (potentially hours or days).

### Q2: What are the trade-offs of implementing token blacklisting?

Blacklisting adds database overhead, increases authentication latency (each request must check the blacklist), and introduces state into a stateless system. However, it provides better security control and the ability to revoke tokens immediately. The performance impact can be mitigated by using an in-memory cache like Redis for the blacklist instead of a full database query.

### Q3: How would you handle expired tokens in the blacklist?

Implement a cleanup job that periodically removes expired tokens from the blacklist to prevent it from growing indefinitely. This can be a scheduled task that runs daily or weekly, or you can use a TTL (Time To Live) feature if using a caching system like Redis. Cleaning up expired tokens maintains database performance and prevents the blacklist from becoming too large.

---

## Exercise 5: Two-Factor Authentication

### Q1: Why is 2FA particularly important for healthcare applications?

2FA provides an additional security layer for accessing sensitive medical records, protecting against data breaches even if passwords are compromised. Healthcare data is highly sensitive and subject to strict privacy regulations. With 2FA, even if a password is stolen through phishing or credential reuse, the attacker would still need the second factor (usually a time-based code from an authenticator app) to access patient data.

### Q2: How would you handle a user losing their 2FA device?

Implement backup codes that users can securely store when enabling 2FA (typically a set of 10 one-time use codes). Provide account recovery options through email verification or support team intervention with proper identity verification. Users should also have the option to disable 2FA through a secure process, and security questions or backup email verification can be used as alternative recovery methods.

### Q3: What are the trade-offs of implementing 2FA vs. using longer passwords?

2FA offers significantly better security than longer passwords alone, as it requires both something you know (password) and something you have (device). This provides defense-in-depth and protects against password theft. However, 2FA adds friction to the login process, requires user education, and can cause user lockouts if they lose their device. Longer passwords improve security but are still vulnerable to phishing and credential stuffing attacks.

---

## Submission Information

**Name:** Jeff Muthomi
**Admission Number:** C027-01-0870/2024
**Date:** 25th July 2026

## GitHub Repository

https://github.com/crimid/health-api

## Screenshots

- Swagger UI: `screenshots/swagger-ui.png`
- PostgreSQL Table: `screenshots/postgres-table.png`
