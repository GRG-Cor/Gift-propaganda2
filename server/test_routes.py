#!/usr/bin/env python3
"""
Тестовый файл для проверки роутов
"""

try:
    from api.telegram import router
    print("✅ Router loaded successfully")
    print("Available routes:")
    for route in router.routes:
        print(f"  {route.methods} {route.path}")
except Exception as e:
    print(f"❌ Error loading router: {e}")
