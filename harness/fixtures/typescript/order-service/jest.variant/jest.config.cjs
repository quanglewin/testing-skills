/**
 * Jest-variant config for framework-detection testing.
 * See note.md in this directory — do NOT install jest dependencies.
 *
 * @type {import('jest').Config}
 */
module.exports = {
  testEnvironment: 'node',
  transform: {
    '^.+\\.tsx?$': ['ts-jest', { useESM: true }],
  },
  extensionsToTreatAsEsm: ['.ts'],
  testMatch: ['**/tests/**/*.test.ts', '**/src/**/*.test.ts'],
};
