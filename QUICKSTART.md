# Route Optimization API - Quickstart

## Endpoint

```
POST https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize
```

## Request

```json
{
  "addresses": [
    "Start Address, City, Country",
    "Stop 1, City, Country",
    "Stop 2, City, Country",
    "End Address, City, Country"
  ]
}
```

- First address = start point (fixed)
- Last address = end point (fixed)
- All middle addresses get reordered optimally

### Optional parameters

| Parameter | Example | Description |
|---|---|---|
| `start_time` | `"2025-01-30T08:00:00Z"` | Route start time (ISO 8601). Default: 23:00 today |
| `objective` | `"minimize_time"` | `minimize_time` / `minimize_distance` / `minimize_cost` |
| `service_time_minutes` | `5` | Time spent at each stop in minutes. Default: 3 |
| `priority_addresses` | see below | Prioritize specific stops for early delivery |

Priority example:

```json
{
  "addresses": ["Start, Berlin", "VIP Client, Munich", "Regular, Hamburg", "End, Frankfurt"],
  "start_time": "2025-01-30T07:00:00Z",
  "objective": "minimize_distance",
  "service_time_minutes": 5,
  "priority_addresses": [
    {
      "address": "VIP Client, Munich",
      "priority_level": "high",
      "preferred_time_window": "early"
    }
  ]
}
```

`priority_level`: `critical_high` | `high` | `medium` | `low` | `critical_low`
`preferred_time_window`: `earliest` | `early` | `middle` | `late` | `latest`

## Response (key fields)

```json
{
  "success": true,
  "optimized_addresses": [
    "Start Address, City, Country",
    "Stop 2, City, Country",
    "Stop 1, City, Country",
    "End Address, City, Country"
  ],
  "route_indices": [0, 2, 1, 3],
  "address_coordinates": {
    "Start Address, City, Country": { "latitude": 52.52, "longitude": 13.40 }
  },
  "timing_info": {
    "vehicle_start_time": "2025-01-30T08:00:00Z",
    "vehicle_end_time": "2025-01-30T11:30:00Z",
    "total_duration_minutes": 210.0
  },
  "optimization_info": {
    "total_distance_km": 45.0,
    "total_time_minutes": 210.0
  },
  "visit_schedule": [
    {
      "stop_number": 1,
      "address": "Start Address, City, Country",
      "arrival_time": "2025-01-30T08:00:00Z",
      "stop_type": "Start"
    }
  ]
}
```

## cURL

```bash
curl -X POST https://items-routes-route-optimisation-dot-maibach-items-routes.ew.r.appspot.com/api/optimize \
  -H "Content-Type: application/json" \
  -d '{
    "addresses": [
      "Neumarkter Str. 39, 90584 Allersberg, Deutschland",
      "Kolpingstr. 2, 90584 Allersberg, Deutschland",
      "Dietkirchen 13, 92367 Pilsach, Deutschland",
      "Seelstr. 20, 92318 Neumarkt, Deutschland"
    ]
  }'
```
