#!/usr/bin/env node
import "source-map-support/register";
import * as cdk from "aws-cdk-lib";
import { RecipehubStack } from "../lib/recipehub-stack";
import * as dotenv from "dotenv";
import * as path from "path";

// Load environment variables from backend .env
dotenv.config({ path: path.join(__dirname, "../../.env") });

const app = new cdk.App();

new RecipehubStack(app, "RecipehubBackendStack", {
  env: {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION || "us-east-1",
  },
  // Pass env vars to the stack
  databaseUrl: process.env.DATABASE_URL!,
  secretKey: process.env.SECRET_KEY!,
  openaiApiKey: process.env.OPENAI_API_KEY!,
});
