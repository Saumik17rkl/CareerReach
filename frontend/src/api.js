const BASE_URL = 'https://careerreach.onrender.com';

async function request(path) {
  const response = await fetch(`${BASE_URL}${path}`);
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }
  return response.json();
}

export const fetchSheets = () => request('/contacts/sheets');
export const fetchContactsBySheet = (sheet) => request(`/contacts?sheet=${encodeURIComponent(sheet)}`);
export const fetchContactById = (id) => request(`/contacts/${id}`);
