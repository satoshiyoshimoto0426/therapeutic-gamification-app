# LINE Bot Service

LINE Bot interface for daily interactions in the therapeutic gamification app.

## Features

### Core Functionality
- **Morning Task Presentation**: Interactive Flex Messages showing daily tasks with one-tap completion
- **Evening Story Delivery**: Rich story content delivery with therapeutic narratives
- **Real-time Notifications**: Pomodoro timer alerts, break reminders, and hyperfocus warnings
- **FCM Fallback**: Firebase Cloud Messaging when LINE is unavailable

### LINE Bot Integration
- LINE Messaging API webhook handling
- Flex Message templates for rich content
- Postback event handling for user interactions
- Push message delivery for proactive notifications

### Notification Types
- 🍅 **Pomodoro**: 25-minute work session alerts
- ☕ **Break**: 5-minute break reminders  
- ⚠️ **Hyperfocus**: 60-minute continuous work warnings
- 📖 **Story**: Evening story content delivery

## API Endpoints

### Webhook
- `POST /webhook` - LINE Bot webhook for message events

### Notifications
- `POST /notifications/send` - Send notification via LINE or FCM fallback

### Task Management
- `POST /tasks/complete` - Complete task via API

### Health Check
- `GET /health` - Service health status

## Environment Variables

```bash
LINE_CHANNEL_ACCESS_TOKEN=your_line_channel_access_token
LINE_CHANNEL_SECRET=your_line_channel_secret
WEBHOOK_URL=your_webhook_url
TASK_MGMT_URL=http://localhost:8003
AI_STORY_URL=http://localhost:8005
ADHD_SUPPORT_URL=http://localhost:8006
```

## Usage Examples

### Morning Task Presentation
Users can request their daily tasks by sending "タスク" or "task":

```
User: タスク
Bot: [Flex Message with task list and completion buttons]
```

### Evening Story Delivery
Users can request evening stories by sending "物語" or "story":

```
User: 物語
Bot: [Flex Message with therapeutic story content]
```

### One-Tap Task Completion
Tasks include completion buttons that trigger postback events:

```
[Task: 朝の運動] [完了] ← User taps this
Bot: タスク完了！お疲れ様でした 🎉
```

## Integration with Other Services

### Task Management Service
- Fetches daily tasks via `/mandala/{uid}/daily-tasks`
- Completes tasks via `/tasks/{task_id}/complete`

### AI Story Service  
- Generates evening stories via `/ai/story/v2/generate`
- Provides therapeutic narrative content

### ADHD Support Service
- Receives Pomodoro timer notifications
- Handles hyperfocus detection alerts

## Testing

Run the test suite:
```bash
python -m pytest test_line_bot.py -v
```

Validate implementation:
```bash
python validate_implementation.py
```

## Architecture

```
LINE Bot Service
├── Webhook Handler
│   ├── Text Message Events
│   ├── Postback Events
│   └── Signature Validation
├── Message Templates
│   ├── Morning Task Flex Messages
│   ├── Evening Story Flex Messages
│   └── Notification Messages
├── Service Integration
│   ├── Task Management API
│   ├── AI Story Generation API
│   └── ADHD Support API
└── Fallback Mechanisms
    ├── FCM Notifications
    └── Error Handling
```

## Therapeutic Design Considerations

### ADHD-Friendly Features
- **One-Screen, One-Action**: Simple task completion with single tap
- **Visual Clarity**: Clear Flex Message layouts with minimal cognitive load
- **Immediate Feedback**: Instant confirmation of task completion
- **Consistent Timing**: Regular morning/evening interaction patterns

### Engagement Mechanisms
- **Rich Media**: Flex Messages with visual appeal
- **Gamification**: Task completion celebrations
- **Storytelling**: Evening narrative delivery for emotional engagement
- **Proactive Support**: Timer-based notifications and reminders

## Error Handling

### LINE API Failures
- Automatic fallback to Firebase Cloud Messaging
- Graceful degradation of rich content to simple text
- Retry mechanisms for transient failures

### Service Integration Failures
- Default responses when external services unavailable
- Cached content for offline scenarios
- User-friendly error messages

## Security

### Webhook Security
- LINE signature validation for all incoming requests
- Request body verification
- Rate limiting protection

### Data Protection
- No sensitive user data stored locally
- Secure communication with backend services
- Audit logging for all user interactions