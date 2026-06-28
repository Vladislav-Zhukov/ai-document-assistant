export type TokenResponse = {
  access_token: string;
  refresh_token: string;
  token_type: string;
};

export type UserRead = {
  id: number;
  email: string;
  is_active: boolean;
  created_at: string;
};