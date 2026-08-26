# Source adapters

Add permitted listing feeds or public inventory sources here.

Each adapter should:

1. Implement `ListingSource`.
2. Return normalised `VehicleListing` objects.
3. Keep source-specific parsing in the adapter.
4. Never bypass CAPTCHAs, bot protection, paywalls or authentication.
5. Use conservative request rates and respect applicable terms.

The demo adapter is intentionally included so the full pipeline can be tested before a live source is configured.
