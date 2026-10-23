import type { components } from './generated/api'

// This must fail under the same compiler options used by the application.
// @ts-expect-error Health.status is a required non-null literal.
const invalidHealth: components['schemas']['Health'] = { status: null, contract_version: 'v1' }
void invalidHealth
