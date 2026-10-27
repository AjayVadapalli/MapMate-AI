import { NextRequest, NextResponse } from 'next/server';

export const dynamic = 'force-dynamic';

export async function GET() {
  try {
    const adkServerUrl = (process.env.ADK_SERVER_URL || 'http://localhost:8000').replace(/\/+$/, '');
    // Test connectivity to ADK server using /list-apps endpoint
    const response = await fetch(`${adkServerUrl}/list-apps`, {
      method: 'GET',
      cache: 'no-store',
    });
    
    if (response.ok) {
      const apps = await response.json();
      return NextResponse.json(
        { 
          status: 'connected', 
          adkServerStatus: response.status,
          message: 'ADK server is reachable',
          availableApps: apps
        },
        {
          headers: {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
          },
        }
      );
    } else {
      throw new Error(`Server returned ${response.status}`);
    }
  } catch (error) {
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { 
        status: 'disconnected', 
        error: 'Cannot reach ADK server',
        message: `ADK server is not reachable at ${process.env.ADK_SERVER_URL || 'http://localhost:8000'}: ${errorMessage}`
      },
      { 
        status: 500,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'GET, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      }
    );
  }
}
