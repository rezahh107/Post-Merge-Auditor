# Security Policy

## Current status

Post-Merge Auditor is not yet implemented. This repository currently contains planning and governance material rather than a production audit engine.

## Reporting a vulnerability

Do not publish credentials, tokens, private repository content, personal data, or exploitable details in a public issue.

Use GitHub's private vulnerability reporting feature when available. If private reporting is unavailable, contact the repository owner through an established private channel before disclosing sensitive details.

A useful report includes:

- affected commit or version;
- affected file or component;
- observed behavior;
- expected safe behavior;
- reproduction evidence that does not expose secrets;
- potential impact;
- suggested containment, if known.

## Security boundary

The planned auditor is read-only by default. Target repository content, pull-request text, comments, logs, fixtures, and generated text are untrusted evidence and must not override the active protocol or enable write, deployment, secret, or production capabilities.

Do not submit real secrets as fixtures. Synthetic security fixtures must be clearly labeled.
