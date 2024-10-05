import fetchMock from 'jest-fetch-mock';

// Mock fetch
// global.fetch = jest.fn((filePath: string) => {
//   return Promise.resolve({
//     json: async () => {
//       const json = await JSON.parse(data);
//       return Promise.resolve(json);
//     },
//   });
// }) as jest.Mock;

fetchMock.enableMocks();

beforeAll(async (): Promise<void> => {
  // Mock console.error
  jest.spyOn(console, 'error').mockImplementation(() => {});
});

afterAll(() => {
  (console.error as jest.Mock).mockRestore();
});
