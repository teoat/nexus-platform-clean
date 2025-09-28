#!/bin/bash

# NEXUS Platform Performance Test Suite
echo "🚀 NEXUS Platform Performance Testing"
echo "====================================="

# Test API Performance
echo "📊 Testing Backend API Performance..."
for i in {1..100}; do
  curl -s -w "%{time_total}\n" -o /dev/null http://localhost:8000/health
done | awk '{sum+=$1; count++} END {print "Average response time: " sum/count "s"}'

# Test Frontend Performance  
echo "📊 Testing Frontend Performance..."
for i in {1..50}; do
  curl -s -w "%{time_total}\n" -o /dev/null http://localhost:3000/
done | awk '{sum+=$1; count++} END {print "Average response time: " sum/count "s"}'

# Test Nginx Proxy Performance
echo "📊 Testing Nginx Proxy Performance..."
for i in {1..50}; do
  curl -s -w "%{time_total}\n" -o /dev/null http://localhost:80/
done | awk '{sum+=$1; count++} END {print "Average response time: " sum/count "s"}'

echo "✅ Performance testing completed!"
