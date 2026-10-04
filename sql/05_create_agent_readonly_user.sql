-- Run once as ADMIN to create the least-privilege runtime user.
-- Replace only this placeholder in your local session;
-- never commit the resulting password or a Wallet.
CREATE USER &AGENT_SCHEMA IDENTIFIED BY "<LSF_AGENT_PASSWORD>";
GRANT CREATE SESSION TO &AGENT_SCHEMA;
-- Run sql/05_grant_agent_readonly.sql separately as ADB_USER.
