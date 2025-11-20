import { Context } from "@netlify/functions";
import { neon } from "@netlify/neon";

export default async (req: Request, context: Context) => {
  try {
    // Initialize Neon client - automatically uses NETLIFY_DATABASE_URL
    const sql = neon();

    // Example query - adjust based on your schema
    // const result = await sql`SELECT * FROM coins LIMIT 10`;

    return new Response(
      JSON.stringify({
        message: "Database connection available",
        timestamp: new Date().toISOString(),
        // data: result,
      }),
      {
        status: 200,
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
  } catch (error) {
    console.error("Database error:", error);
    return new Response(
      JSON.stringify({
        error: "Database connection failed",
        message: error instanceof Error ? error.message : "Unknown error",
      }),
      {
        status: 500,
        headers: {
          "Content-Type": "application/json",
        },
      }
    );
  }
};
