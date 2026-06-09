-- WaterForAll CV module database schema
-- Run once against the waterforall_cv database after RDS provisioning.

CREATE TABLE IF NOT EXISTS cv_image_uploads (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    s3_key      TEXT NOT NULL,
    image_type  TEXT NOT NULL CHECK (image_type IN ('test_strip', 'water_sample')),
    upload_ts   TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    status      TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed'))
);

CREATE TABLE IF NOT EXISTS cv_test_strip_results (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id           UUID NOT NULL REFERENCES cv_image_uploads(id),
    kit_id              TEXT NOT NULL,
    overall_confidence  REAL NOT NULL,
    image_quality_json  JSONB NOT NULL,
    result_json         JSONB NOT NULL,
    created_ts          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cv_water_appearance_results (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id           UUID NOT NULL REFERENCES cv_image_uploads(id),
    appearance_json     JSONB NOT NULL,
    overall_confidence  REAL NOT NULL,
    created_ts          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS cv_processing_errors (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    upload_id     UUID REFERENCES cv_image_uploads(id),
    error_message TEXT NOT NULL,
    traceback     TEXT,
    created_ts    TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
