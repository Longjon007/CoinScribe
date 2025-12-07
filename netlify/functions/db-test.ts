import { Context } from "@netlify/functions";
import { neon } from "@netlify/neon";

export default async (_req: Request, _context: Context) => {
  const startTime = performance.now();
  
  try {
    // Initialize Neon client - automatically uses NETLIFY_DATABASE_URL
    const _sql = neon();

    // Example query - adjust based on your schema
    // const result = await sql`SELECT * FROM coins LIMIT 10`;

    const responseTime = performance.now() - startTime;

    return new Response(
      JSON.stringify({
        message: "Database connection available",
        timestamp: new Date().toISOString(),
        responseTime: `${responseTime.toFixed(2)}ms`,
        // data: result,
      }),
      {
        status: 200,
        headers: {
          "Content-Type": "application/json",
          "Cache-Control": "public, max-age=60", // Cache for 60 seconds
        },
      }
    );
  } catch (error) {
    const responseTime = performance.now() - startTime;
    
    // Log detailed error information for debugging
    const errorDetails = {
      message: error instanceof Error ? error.message : "Unknown error",
      stack: error instanceof Error ? error.stack : undefined,
      timestamp: new Date().toISOString(),
      responseTime: `${responseTime.toFixed(2)}ms`,
    };
    
    console.error("Database error:", errorDetails);
    
    return new Response(
      JSON.stringify({
        error: "Database connection failed",
        message: error instanceof Error ? error.message : "Unknown error",
        timestamp: new Date().toISOString(),
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
