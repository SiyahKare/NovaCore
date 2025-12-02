#!/bin/bash
# NovaCore Production Durdurma Scripti

echo "🛑 NovaCore Production Durduruluyor..."

# PID dosyalarından oku
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo "✅ Backend durduruldu (PID: $BACKEND_PID)"
    fi
    rm .backend.pid
fi

if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo "✅ Frontend durduruldu (PID: $FRONTEND_PID)"
    fi
    rm .frontend.pid
fi

if [ -f ".tunnel.pid" ]; then
    TUNNEL_PID=$(cat .tunnel.pid)
    if kill -0 $TUNNEL_PID 2>/dev/null; then
        kill $TUNNEL_PID
        echo "✅ Cloudflare Tunnel durduruldu (PID: $TUNNEL_PID)"
    fi
    rm .tunnel.pid
fi

# Fallback: process name ile kill
pkill -f "uvicorn app.main:app" 2>/dev/null && echo "✅ Backend process'leri temizlendi"
pkill -f "next-server" 2>/dev/null && echo "✅ Frontend process'leri temizlendi"
pkill -f "cloudflared tunnel" 2>/dev/null && echo "✅ Tunnel process'leri temizlendi"

echo "✅ Tüm servisler durduruldu"

