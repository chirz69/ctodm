const API_URL =
  "http://127.0.0.1:8000";


function getToken() {

  return localStorage.getItem(
    "comment2dm_token"
  );

}


async function request(
  endpoint,
  options = {}
) {

  const token = getToken();


  const headers = {
    "Content-Type":
      "application/json",

    ...(options.headers || {}),
  };


  if (token) {

    headers[
      "Authorization"
    ] = `Bearer ${token}`;

  }


  const response = await fetch(

    `${API_URL}${endpoint}`,

    {
      ...options,

      headers,
    }

  );


  const data =
    await response.json();


  if (!response.ok) {

    throw new Error(

      data.detail ||
      data.error ||
      "Request failed."

    );

  }


  return data;

}


export async function register(
  email,
  password
) {

  return request(
    "/api/auth/register",
    {
      method: "POST",

      body: JSON.stringify({
        email,
        password,
      }),
    }
  );

}


export async function login(
  email,
  password
) {

  return request(
    "/api/auth/login",
    {
      method: "POST",

      body: JSON.stringify({
        email,
        password,
      }),
    }
  );

}


export async function getMe() {

  return request(
    "/api/auth/me"
  );

}


export async function getInstagramAccounts() {

  return request(
    "/api/instagram/accounts"
  );

}


export async function getCampaigns() {

  return request(
    "/api/campaigns"
  );

}


export async function createCampaign(
  campaign
) {

  return request(
    "/api/campaigns",
    {
      method: "POST",

      body: JSON.stringify(
        campaign
      ),
    }
  );

}


export async function deleteCampaign(
  id
) {

  return request(
    `/api/campaigns/${id}`,
    {
      method: "DELETE",
    }
  );

}


export async function logout() {

  const result =
    await request(
      "/api/auth/logout",
      {
        method: "POST",
      }
    );


  localStorage.removeItem(
    "comment2dm_token"
  );


  return result;

}


export function getInstagramConnectUrl() {

  return `${API_URL}/auth/instagram`;

}


export { API_URL };