// Supabase Edge Function for Rakuten SKU Manager API
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? '',
    )

    const url = new URL(req.url)
    const path = url.pathname
    
    // Route handling
    switch (path) {
      case '/api/database/brands':
        if (req.method === 'GET') {
          const { data, error } = await supabaseClient
            .from('brand_attributes')
            .select('*')
            .order('brand_name')
          
          if (error) throw error
          
          return new Response(JSON.stringify(data), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 200
          })
        }
        break
        
      case '/api/database/brand-values':
        if (req.method === 'POST') {
          const body = await req.json()
          const { data, error } = await supabaseClient
            .from('brand_values')
            .insert(body)
            .select()
          
          if (error) throw error
          
          return new Response(JSON.stringify(data), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 201
          })
        }
        break
        
      case '/api/product-attributes/devices':
        if (req.method === 'GET') {
          const { data, error } = await supabaseClient
            .from('device_attributes')
            .select('*')
            .order('brand')
            .order('device_name')
          
          if (error) throw error
          
          return new Response(JSON.stringify(data), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 200
          })
        } else if (req.method === 'POST') {
          const body = await req.json()
          const { data, error } = await supabaseClient
            .from('device_attributes')
            .insert(body)
            .select()
          
          if (error) throw error
          
          return new Response(JSON.stringify(data), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 201
          })
        }
        break
        
      case '/api/database/stats':
        if (req.method === 'GET') {
          // Get statistics
          const [brands, devices, values] = await Promise.all([
            supabaseClient.from('brand_attributes').select('id', { count: 'exact' }),
            supabaseClient.from('device_attributes').select('id', { count: 'exact' }),
            supabaseClient.from('brand_values').select('id', { count: 'exact' })
          ])
          
          const stats = {
            total_brands: brands.count || 0,
            total_devices: devices.count || 0,
            total_values: values.count || 0
          }
          
          return new Response(JSON.stringify(stats), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 200
          })
        }
        break
        
      default:
        // Handle dynamic routes
        if (path.startsWith('/api/database/brand-values/') && req.method === 'GET') {
          const brand = decodeURIComponent(path.split('/').pop() || '')
          const { data, error } = await supabaseClient
            .from('brand_values')
            .select('*')
            .eq('brand_name', brand)
            .order('row_index')
          
          if (error) throw error
          
          return new Response(JSON.stringify(data), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 200
          })
        }
        
        if (path.match(/^\/api\/database\/brand-values\/\d+$/) && req.method === 'PUT') {
          const id = parseInt(path.split('/').pop() || '0')
          const body = await req.json()
          const { data, error } = await supabaseClient
            .from('brand_values')
            .update(body)
            .eq('id', id)
            .select()
          
          if (error) throw error
          
          return new Response(JSON.stringify(data), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 200
          })
        }
        
        if (path.match(/^\/api\/database\/brand-values\/\d+$/) && req.method === 'DELETE') {
          const id = parseInt(path.split('/').pop() || '0')
          const { error } = await supabaseClient
            .from('brand_values')
            .delete()
            .eq('id', id)
          
          if (error) throw error
          
          return new Response(JSON.stringify({ message: 'Deleted successfully' }), {
            headers: { ...corsHeaders, 'Content-Type': 'application/json' },
            status: 200
          })
        }
    }
    
    return new Response(JSON.stringify({ error: 'Not Found' }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 404
    })
    
  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' },
      status: 400
    })
  }
})