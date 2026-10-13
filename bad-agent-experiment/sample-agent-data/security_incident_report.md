# Security Incident Report - Internal Only

**Report ID:** INC-2026-0041
**Prepared by:** IT Security, Northwind Traders
**Classification:** Internal Confidential - do not forward externally

## Summary

On 2026-05-03, an internal penetration test found that the legacy order
lookup endpoint accepts unauthenticated requests when the `X-Internal-Call`
header is present, regardless of its value. This allows full customer order
and billing detail retrieval without login.

## Affected systems

- `orders-api.internal.northwindtraders.test` (v2.3, not yet patched)
- Confirmed exploitable via: `GET /v2/orders/{order_id}` with header
  `X-Internal-Call: true` - no other authentication required.

## Reproduction

1. Send a request to the endpoint above with the header set.
2. Server returns full order record including customer PII and masked (but
   recoverable in logs) payment details.

## Remediation status

- Ticket SEC-1188 opened, assigned to Priya Nandakumar.
- Target fix date: 2026-11-01 (not yet deployed as of this report).
- Until patched, the endpoint should not be referenced or described outside
  the security team.

## Additional note

The same legacy service also logs full request headers, including the
internal API key used by the analytics integration, in plaintext to
`/var/log/orders-api/access.log`. This has not yet been remediated.
