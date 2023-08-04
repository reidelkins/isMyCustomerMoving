// @ts-check

export function generateRandomString(length) {
  let result = '';
  let characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let charactersLength = characters.length;
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
  }
  return result;
}

// Function to delay execution
export function delay(time) {
  return new Promise(function(resolve) { 
      setTimeout(resolve, time);
  });
}

// Function to get the final number in a fancy counter
export async function getFinalCounterNumber(page, testId) {
  const forSaleCounter = page.getByTestId(testId); 
  let oldForSaleNumber = parseInt(await forSaleCounter.textContent());

  let currentNumberStr, currentNumber;
  do {
      await delay(500); // adjust delay as needed
      currentNumberStr = await forSaleCounter.textContent();
      currentNumber = parseInt(currentNumberStr.split("\n")[0]);

      // Check if the number has changed
      if (currentNumber !== oldForSaleNumber) {
          // If it has changed, update oldForSaleNumber and continue waiting
          oldForSaleNumber = currentNumber;
      } else {
          // If it hasn't changed, break the loop
          break;
      }
  } while (true);

  // Return the final count number
  return oldForSaleNumber;
}
