// MongoDB initialization script for Agentic-Ads
// This script runs when the MongoDB container starts for the first time

// Create collections with proper indexes
db = db.getSiblingDB('agentic_ads');

// Generation history collection
db.createCollection('generation_history');
db.generation_history.createIndex({ "id": 1 }, { unique: true });
db.generation_history.createIndex({ "date": 1 });
db.generation_history.createIndex({ "platform": 1 });
db.generation_history.createIndex({ "status": 1 });

// Feedback collection
db.createCollection('feedback');
db.feedback.createIndex({ "id": 1 }, { unique: true });
db.feedback.createIndex({ "email": 1 });
db.feedback.createIndex({ "rating": 1 });
db.feedback.createIndex({ "date": 1 });
db.feedback.createIndex({ "platform": 1 });

// Users collection (for future user management)
db.createCollection('users');
db.users.createIndex({ "username": 1 }, { unique: true });
db.users.createIndex({ "email": 1 }, { unique: true });

// Analytics collection (for storing aggregated data)
db.createCollection('analytics');
db.analytics.createIndex({ "date": 1 });
db.analytics.createIndex({ "type": 1 });

// Insert sample data for development
db.generation_history.insertMany([
  {
    id: 1,
    date: new Date().toISOString().split('T')[0],
    time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    platform: "Instagram",
    tone: "Professional",
    adText: "🚀 Ready to level up your business? Our premium solutions deliver exceptional results!",
    outputs: "Text, Poster, Video",
    status: "Completed"
  },
  {
    id: 2,
    date: new Date().toISOString().split('T')[0],
    time: new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }),
    platform: "LinkedIn",
    tone: "Formal",
    adText: "Professional development opportunities for career advancement.",
    outputs: "Text, Poster",
    status: "Completed"
  }
]);

db.feedback.insertMany([
  {
    id: 1,
    email: "test@example.com",
    message: "Great platform! The AI-generated content is impressive.",
    rating: 5,
    action: "General feedback",
    date: new Date().toISOString().split('T')[0],
    platform: "Instagram"
  },
  {
    id: 2,
    email: "user@company.com",
    message: "Logo integration worked perfectly!",
    rating: 5,
    action: "Logo upload",
    date: new Date().toISOString().split('T')[0],
    platform: "LinkedIn"
  }
]);

print("✅ Agentic-Ads database initialized successfully!");
print(`📊 Inserted ${db.generation_history.countDocuments()} generation records`);
print(`💬 Inserted ${db.feedback.countDocuments()} feedback records`);
