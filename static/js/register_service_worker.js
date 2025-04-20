'use strict';

function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding)
    .replace(/\-/g, '+')
    .replace(/_/g, '/');

  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);

  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

function updateSubscriptionOnServer(subscription, apiEndpoint) {
  // TODO: Send subscription to application server

  return fetch(apiEndpoint, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      subscription_json: JSON.stringify(subscription)
    })
  });

}

async function subscribeUser(swRegistration, applicationServerPublicKey, apiEndpoint) {
    if (swRegistration.active) {
        console.log("executing Sub.")
      return executeSubscription(swRegistration, applicationServerPublicKey, apiEndpoint);
    } else {
      swRegistration.addEventListener('statechange', function(event) {
        if (event.target.state === 'activated') {
            console.log('waiting and sub.')
          return executeSubscription(swRegistration, applicationServerPublicKey, apiEndpoint);
        }
      });
    }
}
  
async function executeSubscription(swRegistration, applicationServerPublicKey, apiEndpoint) {
      const applicationServerKey = urlB64ToUint8Array(applicationServerPublicKey);
      try {
        const subscription = await swRegistration.pushManager.subscribe({
          userVisibleOnly: true,
          applicationServerKey: applicationServerKey
        });
        console.log('User is subscribed.');
        const response = await updateSubscriptionOnServer(subscription, apiEndpoint);
        if (!response.ok) throw new Error('Bad status code from server.');
        const responseData = await response.json();
        if (responseData.status !== "success") throw new Error('Bad response from server.');
        console.log(responseData);
      } catch (err) {
        console.log('Failed to subscribe the user: ', err);
        console.log(err.stack);
      }
}


async function registerServiceWorker(serviceWorkerUrl, applicationServerPublicKey, apiEndpoint){
  let swRegistration = null;
  if ('serviceWorker' in navigator && 'PushManager' in window) {
    console.log('Service Worker and Push is supported');

    try {
        const swReg = await navigator.serviceWorker.register(serviceWorkerUrl);
        console.log('Service Worker is registered', swReg);
        await subscribeUser(swReg, applicationServerPublicKey, apiEndpoint);
        swRegistration = swReg;  
        } catch (error) {
        console.error('Service Worker Error', error);
    }
  } else {
    console.warn('Push messaging is not supported');
  } 
  return swRegistration;
}