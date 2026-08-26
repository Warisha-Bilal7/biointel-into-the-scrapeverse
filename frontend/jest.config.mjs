import nextJest from 'next/jest'

const createNextConfig = nextJest({ dir: './' })

const customJestConfig = {
  setupFilesAfterEnv: ['<rootDir>/setupTests.ts'],
  testEnvironment: 'jsdom',
  // Map module name aliases if you have any (e.g. @/*, etc.)
  // moduleNameMapper: {
  //   '^@/components/(.*)$': '<rootDir>/components/$1',
  //   '^@/lib/(.*)$': '<rootDir>/lib/$1',
  // },
  // Note: next/jest automatically handles Next.js module aliases
  // through Next.js's module system. If you've configured
  // PathRewrites in next.config.js, they'll be picked up automatically.
}

export default createNextConfig(customJestConfig)