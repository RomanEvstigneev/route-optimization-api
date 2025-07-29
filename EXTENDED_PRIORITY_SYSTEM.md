# Extended Priority System Architecture

## Overview

The Extended Priority System enhances the route optimization service with granular priority control, extended time windows, and custom penalty costs while maintaining full backwards compatibility with existing API calls.

## 🎯 Key Features

### Extended Priority Levels
- **critical_high**: Extreme priority with maximum penalty costs (1000.0 default)
- **high**: High priority (500.0 default) 
- **medium**: Standard priority (100.0 default)
- **low**: Low priority (25.0 default)
- **critical_low**: Minimal priority (5.0 default)

### Extended Time Windows
- **earliest**: 0-1.5 hours from start time
- **early**: 1.5-3 hours from start time
- **middle**: 3-4.5 hours from start time  
- **late**: 4.5-6 hours from start time
- **latest**: 6-8 hours from start time

### Custom Penalty Costs
Users can override default penalty costs with custom values for fine-tuned optimization control.

## 📋 API Documentation

### Input JSON Schema

```json
{
  "addresses": [
    "Start Address",
    "Priority Address 1", 
    "Priority Address 2",
    "End Address"
  ],
  "priority_addresses": [
    {
      "address": "Priority Address 1",
      "priority_level": "critical_high|high|medium|low|critical_low",
      "preferred_time_window": "earliest|early|middle|late|latest", 
      "penalty_cost": 150.0  // Optional custom penalty cost
    }
  ],
  "start_time": "2024-01-01T08:00:00Z",
  "objective": "minimize_time|minimize_distance|minimize_cost",
  "service_time_minutes": 3,
  "route_name": "Custom Route Name"
}
```

### Output JSON Schema

The response includes enhanced priority information:

```json
{
  "success": true,
  "priority_addresses_config": [
    {
      "address": "Priority Address 1",
      "priority_level": "critical_high",
      "preferred_time_window": "earliest",
      "penalty_cost": 150.0,
      "resolved_cost_per_hour_after": 150.0,
      "time_window_applied": true,
      "address_index": 1
    }
  ],
  "priority_statistics": {
    "total_priority_addresses": 3,
    "priority_breakdown": {
      "critical_high": 1,
      "high": 1, 
      "medium": 1,
      "low": 0,
      "critical_low": 0
    },
    "time_window_breakdown": {
      "earliest": 1,
      "early": 1,
      "middle": 1,
      "late": 0,
      "latest": 0
    }
  },
  "priority_system_version": "2.0"
}
```

## 🔄 Backwards Compatibility

### Legacy Format Support
Existing API calls using the old format continue to work:

```json
{
  "priority_addresses": [
    {
      "address": "Address",
      "priority_level": "high",  // Maps to new "high"
      "preferred_time_window": "early"  // Maps to new "early"
    }
  ]
}
```

### Automatic Mapping
- Legacy `"high"` → `"high"`
- Legacy `"medium"` → `"medium"` 
- Legacy `"low"` → `"low"`
- Legacy `"early"` → `"early"`
- Legacy `"middle"` → `"middle"`
- Legacy `"late"` → `"late"`

### Default Values
Missing fields are automatically populated:
- `priority_level`: defaults to `"medium"`
- `preferred_time_window`: defaults to `"middle"`
- `penalty_cost`: uses system defaults based on priority level

## ⚙️ Configuration Constants

### Priority Penalty Costs
```python
PRIORITY_PENALTY_COSTS = {
    "critical_high": 1000.0,  # Extreme penalty
    "high": 500.0,            # High penalty  
    "medium": 100.0,          # Medium penalty
    "low": 25.0,              # Low penalty
    "critical_low": 5.0       # Minimal penalty
}
```

### Time Window Offsets (hours from start)
```python
TIME_WINDOW_OFFSETS = {
    "earliest": (0, 1.5),    # 0-1.5 hours
    "early": (1.5, 3),       # 1.5-3 hours
    "middle": (3, 4.5),      # 3-4.5 hours  
    "late": (4.5, 6),        # 4.5-6 hours
    "latest": (6, 8)         # 6-8 hours
}
```

## 🛡️ Validation Strategy

### Input Validation
- **Address Existence**: Priority addresses must exist in the addresses list
- **Start/End Points**: Cannot prioritize start or end addresses
- **Priority Levels**: Must be valid enum values with legacy support
- **Time Windows**: Must be valid enum values with legacy support  
- **Penalty Costs**: Must be positive numbers if provided
- **Duplicates**: No duplicate priority addresses allowed

### Error Messages
Clear, actionable error messages for validation failures:

```json
{
  "error": "Priority address configuration at index 0: Invalid priority_level 'extreme'. Valid values: ['critical_high', 'high', 'medium', 'low', 'critical_low', 'high', 'medium', 'low']",
  "success": false
}
```

## 🚀 Usage Examples

### Example 1: Basic Extended Priority
```json
{
  "addresses": ["Start", "Hospital", "Office", "End"],
  "priority_addresses": [
    {
      "address": "Hospital",
      "priority_level": "critical_high",
      "preferred_time_window": "earliest"
    }
  ]
}
```

### Example 2: Custom Penalty Costs
```json
{
  "priority_addresses": [
    {
      "address": "VIP Client",
      "priority_level": "high", 
      "preferred_time_window": "early",
      "penalty_cost": 750.0
    }
  ]
}
```

### Example 3: Mixed Priorities
```json
{
  "priority_addresses": [
    {
      "address": "Emergency Delivery",
      "priority_level": "critical_high",
      "preferred_time_window": "earliest",
      "penalty_cost": 2000.0
    },
    {
      "address": "Regular Customer",
      "priority_level": "medium",
      "preferred_time_window": "middle"
    },
    {
      "address": "Backup Location", 
      "priority_level": "critical_low",
      "preferred_time_window": "latest"
    }
  ]
}
```

## 📊 Priority System Statistics

The enhanced system provides detailed statistics in the response:

- **Total Priority Addresses**: Count of prioritized stops
- **Priority Breakdown**: Count by priority level
- **Time Window Breakdown**: Count by preferred time window
- **Custom Penalty Usage**: How many addresses use custom penalties

## 🔧 Implementation Details

### Architecture Components

1. **PrioritySystemValidator**: Input validation with clear error messages
2. **ExtendedPriorityTimeWindowCreator**: Enhanced time window creation
3. **DefaultValueHandler**: Backwards compatibility support
4. **PrioritySystemConfig**: Configuration management and statistics

### Function Signatures

The main optimization function maintains backwards compatibility:

```python
def optimize_route_with_api(
    addresses, 
    time_windows_config=None, 
    priority_addresses_config=None,  # Supports both legacy and new formats
    start_time_config=None, 
    objective_config=None, 
    service_time_minutes=3
):
```

### Integration Points

- **Web Interface**: Enhanced HTML template with new priority badges
- **API Endpoint**: Seamless integration with existing `/api/optimize` endpoint
- **Response Enhancement**: Automatic enrichment with priority statistics

## 🎨 UI Enhancements

### Priority Badges
- **critical_high**: Dark red with pulsing animation
- **high**: Red background  
- **medium**: Yellow background
- **low**: Green background
- **critical_low**: Gray background

### Time Window Indicators
Color-coded badges for different time windows:
- **earliest**: Red
- **early**: Orange  
- **middle**: Blue
- **late**: Green
- **latest**: Purple

## 🔍 Monitoring and Logging

Enhanced logging provides visibility into priority system operation:

```
INFO: Applied extended priority time windows for 3 addresses
INFO: Priority breakdown: {'critical_high': 1, 'high': 1, 'medium': 1, 'low': 0, 'critical_low': 0}
INFO: Time window breakdown: {'earliest': 1, 'early': 1, 'middle': 1, 'late': 0, 'latest': 0}
```

## 🧪 Testing Strategy

### Test Cases
1. **Backwards Compatibility**: All existing API calls work unchanged
2. **Extended Features**: New priority levels and time windows function correctly
3. **Input Validation**: Comprehensive error handling with clear messages
4. **Edge Cases**: Duplicate addresses, invalid values, empty configurations
5. **Performance**: Large numbers of priority addresses

### Example Test Data
See `static/extended_example.json` for comprehensive test scenarios.

## 📈 Performance Considerations

- **Validation Overhead**: Minimal impact with efficient enum lookups
- **Memory Usage**: Lightweight dataclasses for configuration
- **API Response Size**: Modest increase with enhanced statistics
- **Processing Time**: No significant impact on optimization performance

## 🛠️ Maintenance and Updates

### Adding New Priority Levels
1. Add to `PriorityLevel` enum
2. Update `PRIORITY_PENALTY_COSTS` mapping
3. Add UI styling in templates
4. Update documentation

### Adding New Time Windows  
1. Add to `TimeWindow` enum
2. Update `TIME_WINDOW_OFFSETS` mapping
3. Add UI styling in templates
4. Update documentation

### Version Compatibility
- **v1.0**: Legacy three-level priority system
- **v2.0**: Extended five-level priority system with enhanced time windows
- Response includes `priority_system_version` field for client compatibility

## 🔐 Security Considerations

- **Input Sanitization**: All user inputs validated and sanitized
- **DoS Protection**: Reasonable limits on priority address counts
- **Data Validation**: Strict type checking and range validation
- **Error Handling**: No sensitive information leaked in error messages