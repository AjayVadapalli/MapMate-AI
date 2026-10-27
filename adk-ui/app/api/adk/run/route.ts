import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const adkServerUrl = (process.env.ADK_SERVER_URL || 'http://localhost:8000').replace(/\/+$/, '');
    
    // Convert from UI format to ADK API format (camelCase to snake_case)
    const adkRequest = {
      app_name: body.appName,
      user_id: body.userId,
      session_id: body.sessionId,
      new_message: body.newMessage,
    };

    // First, ensure session exists
    try {
      await fetch(`${adkServerUrl}/apps/${body.appName}/users/${body.userId}/sessions/${body.sessionId}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ state: {} }),
      });
    } catch (sessionError) {
      // Session might already exist, continue
      console.log('Session creation note:', sessionError);
    }

    // Forward the request to the ADK server with correct format
    const response = await fetch(`${adkServerUrl}/run`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(adkRequest),
    });

    if (!response.ok) {
      const errorText = await response.text();
      const detail = response.status >= 500
        ? 'Check the ADK backend terminal for the underlying agent or model error.'
        : errorText;
      return NextResponse.json(
        { error: `ADK request failed (${response.status}). ${detail}` },
        { status: response.status },
      );
    }

    const data = await response.json();
    
    return NextResponse.json(data, {
      headers: {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'POST, OPTIONS',
        'Access-Control-Allow-Headers': 'Content-Type',
      },
    });
  } catch (error) {
    console.error('Proxy error:', error);
    const errorMessage = error instanceof Error ? error.message : 'Unknown error';
    return NextResponse.json(
      { error: `Could not reach the ADK server at ${process.env.ADK_SERVER_URL || 'http://localhost:8000'}: ${errorMessage}` },
      {
        status: 502,
        headers: {
          'Access-Control-Allow-Origin': '*',
          'Access-Control-Allow-Methods': 'POST, OPTIONS',
          'Access-Control-Allow-Headers': 'Content-Type',
        },
      }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}
