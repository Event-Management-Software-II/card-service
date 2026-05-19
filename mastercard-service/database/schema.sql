CREATE TYPE "CardTransactionStatus" AS ENUM ('approved', 'rejected');

CREATE TABLE cards (
  id        SERIAL PRIMARY KEY,
  pan       VARCHAR(16)    UNIQUE NOT NULL,
  cvv       VARCHAR(4)     NOT NULL,
  expiry    VARCHAR(5)     NOT NULL,
  holder    VARCHAR(100)   NOT NULL,
  balance   DECIMAL(12, 2) NOT NULL DEFAULT 0,
  "isActive" BOOLEAN       NOT NULL DEFAULT true
);

CREATE TABLE card_transactions (
  id               SERIAL PRIMARY KEY,
  "lastFourDigits" VARCHAR(4)             NOT NULL,
  amount           DECIMAL(10, 2)         NOT NULL,
  status           "CardTransactionStatus" NOT NULL,
  "rejectionReason" VARCHAR(255),
  reference        VARCHAR(100),
  "cardHolder"     VARCHAR(100),
  "createdAt"      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ct_status  ON card_transactions(status);
CREATE INDEX idx_ct_created ON card_transactions("createdAt");
