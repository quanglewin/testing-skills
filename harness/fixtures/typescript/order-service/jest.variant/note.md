# Jest Variant

This directory exists to test the **framework-detection** behavior of the
`generate-tests` skill (spec: "TS fixture under both Vitest and Jest detection,
Jest via a config-swapped fixture variant").

The fixture's default test framework is Vitest (`vitest.config.ts` at the
fixture root). To run the eval against **Jest detection** instead, swap the
configs in a temporary copy of the fixture:

1. Copy `jest.variant/jest.config.cjs` to the fixture root as `jest.config.cjs`.
2. Remove (or rename) `vitest.config.ts` at the fixture root.
3. In `package.json`, change the `test` script from `vitest run` to `jest`
   and remove `vitest` from `devDependencies`.

The skill under eval should then detect Jest as the target framework and
generate Jest-style tests (imports, mock APIs, fake timers).

**Do NOT install jest / ts-jest dependencies in this fixture.** The variant
only exercises config-based framework *detection*; the Jest run's hard gates
(compile/pass) are out of scope until Jest deps are deliberately added to a
temp eval copy. Keeping jest out of `devDependencies` keeps the default
Vitest fixture unambiguous.
