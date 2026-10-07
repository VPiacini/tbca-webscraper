-- Valores por 100 g de alimento, na unidade original da TBCA. NULL = não informado pela TBCA.

CREATE TABLE IF NOT EXISTS Produto (
    Produto_id TEXT PRIMARY KEY,  -- código TBCA sem o prefixo BRC, ex.: 0001A
    nome       TEXT NOT NULL,
    categoria  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Macronutrientes (
    Produto_id               TEXT PRIMARY KEY REFERENCES Produto,
    calorias                 NUMERIC,  -- kcal
    carboidratos             NUMERIC,  -- g
    acucares_totais          NUMERIC,  -- g (não existe na TBCA)
    acucares_adicionados     NUMERIC,  -- g
    proteinas                NUMERIC,  -- g
    gorduras_totais          NUMERIC,  -- g
    gorduras_saturadas       NUMERIC,  -- g
    gorduras_monoinsaturadas NUMERIC,  -- g
    gorduras_poliinsaturadas NUMERIC,  -- g
    gorduras_trans           NUMERIC,  -- g
    colesterol               NUMERIC,  -- mg
    fibra                    NUMERIC   -- g
);

CREATE TABLE IF NOT EXISTS Minerais (
    Produto_id TEXT PRIMARY KEY REFERENCES Produto,
    calcio     NUMERIC,  -- mg
    ferro      NUMERIC,  -- mg
    magnesio   NUMERIC,  -- mg
    fosforo    NUMERIC,  -- mg
    potassio   NUMERIC,  -- mg
    sodio      NUMERIC,  -- mg
    zinco      NUMERIC,  -- mg
    cobre      NUMERIC,  -- mg
    manganes   NUMERIC,  -- mg
    selenio    NUMERIC   -- µg
);

CREATE TABLE IF NOT EXISTS Vitaminas (
    Produto_id  TEXT PRIMARY KEY REFERENCES Produto,
    vitaminaA   NUMERIC,  -- µg RAE
    vitaminaE   NUMERIC,  -- mg (alfa-tocoferol)
    vitaminaD   NUMERIC,  -- µg
    vitaminaC   NUMERIC,  -- mg
    vitaminaK   NUMERIC,  -- µg (não existe na TBCA)
    tiamina     NUMERIC,  -- mg
    riboflavina NUMERIC,  -- mg
    niacina     NUMERIC,  -- mg
    vitaminaB6  NUMERIC,  -- mg
    folato      NUMERIC,  -- µg DFE
    vitaminaB12 NUMERIC   -- µg
);
