export default {
  transform: {
    '^.+\\.[t|j]sx?$': 'babel-jest',
  },
  testEnvironment: 'jsdom',
  transformIgnorePatterns: ['/node_modules/'],
  testMatch: ['<rootDir>/tests/**/*.test.tsx'],
  extensionsToTreatAsEsm: ['.ts'],
  moduleNameMapper: {
    '\\.(css|less)$': 'identity-obj-proxy',
  },
  setupFilesAfterEnv: ['./tests/jest.setup.ts'],
};
