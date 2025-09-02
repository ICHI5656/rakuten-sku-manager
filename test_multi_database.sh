#!/bin/bash

echo "================================"
echo "Testing Multi-Database System"
echo "================================"
echo ""

# Test 1: List databases
echo "1. Listing available databases:"
curl -s http://localhost:8000/api/multi-database/databases | python3 -m json.tool
echo ""

# Test 2: Get stats for brand_attributes
echo "2. Brand attributes database stats:"
curl -s http://localhost:8000/api/multi-database/brand_attributes/stats | python3 -m json.tool | head -15
echo ""

# Test 3: Get stats for product_attributes_8
echo "3. Product attributes 8 database stats:"
curl -s http://localhost:8000/api/multi-database/product_attributes_8/stats | python3 -m json.tool | head -15
echo ""

# Test 4: Get tables from product_attributes_8
echo "4. Tables in product_attributes_8:"
curl -s http://localhost:8000/api/multi-database/product_attributes_8/data | python3 -m json.tool
echo ""

# Test 5: Sample data from device_mappings
echo "5. Sample device mappings (first 3 rows):"
curl -s "http://localhost:8000/api/multi-database/product_attributes_8/data?table=device_mappings&limit=3" | python3 -m json.tool | head -30
echo ""

echo "================================"
echo "All tests completed!"
echo "================================"
echo ""
echo "You can now access the multi-database management UI at:"
echo "http://localhost:3000/multi-database"
echo ""
echo "Available interfaces:"
echo "- SKU Processing: http://localhost:3000/"
echo "- Brand Database: http://localhost:3000/database"
echo "- Multi-Database Manager: http://localhost:3000/multi-database"