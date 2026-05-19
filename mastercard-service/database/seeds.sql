INSERT INTO cards (pan, cvv, expiry, holder, balance) VALUES
  ('5412345678901234', '123', '12/26', 'Carlos Mendoza',   1000000.00),
  ('5500005555555559', '456', '06/27', 'Laura Gutierrez',   500000.00),
  ('5105105105105100', '789', '03/28', 'Andres Ramirez',   2000000.00),
  ('5200828282828210', '321', '09/26', 'Maria Torres',      750000.00)
ON CONFLICT (pan) DO NOTHING;
