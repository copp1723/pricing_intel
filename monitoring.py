"""
System monitoring and health check service
Provides real-time monitoring of system components and performance metrics
"""

import time
import psutil
import sqlite3
from datetime import datetime, timedelta
from src.models.user import db
from src.models.vehicle import Vehicle, VehicleScore, VehicleMatch
import logging

class SystemMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.response_times = []
        
    def record_request(self, response_time_ms, success=True):
        """Record API request metrics"""
        self.request_count += 1
        if not success:
            self.error_count += 1
        self.response_times.append(response_time_ms)
        
        # Keep only last 1000 response times
        if len(self.response_times) > 1000:
            self.response_times = self.response_times[-1000:]
    
    def get_system_health(self):
        """Get comprehensive system health metrics"""
        try:
            # Database metrics
            db_metrics = self._get_database_metrics()
            
            # System resource metrics
            system_metrics = self._get_system_metrics()
            
            # API performance metrics
            api_metrics = self._get_api_metrics()
            
            # Service status
            service_status = self._get_service_status()
            
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "healthy" if self._is_system_healthy(db_metrics, system_metrics, api_metrics) else "degraded",
                "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
                "database": db_metrics,
                "system": system_metrics,
                "api": api_metrics,
                "services": service_status
            }
        except Exception as e:
            logging.error(f"Error getting system health: {str(e)}")
            return {
                "timestamp": datetime.now().isoformat(),
                "overall_status": "error",
                "error": str(e)
            }
    
    def _get_database_metrics(self):
        """Get database performance and status metrics"""
        try:
            # Count records
            total_vehicles = Vehicle.query.count()
            total_scores = VehicleScore.query.count()
            total_matches = VehicleMatch.query.count()
            
            # Recent activity (last 24 hours)
            yesterday = datetime.now() - timedelta(days=1)
            recent_vehicles = Vehicle.query.filter(Vehicle.created_at >= yesterday).count()
            recent_scores = VehicleScore.query.filter(VehicleScore.created_at >= yesterday).count()
            
            # Database size
            db_path = 'src/database/app.db'
            db_size_mb = 0
            try:
                import os
                if os.path.exists(db_path):
                    db_size_mb = os.path.getsize(db_path) / (1024 * 1024)
            except:
                pass
            
            return {
                "status": "connected",
                "total_vehicles": total_vehicles,
                "total_scores": total_scores,
                "total_matches": total_matches,
                "recent_vehicles_24h": recent_vehicles,
                "recent_scores_24h": recent_scores,
                "database_size_mb": round(db_size_mb, 2)
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def _get_system_metrics(self):
        """Get system resource metrics"""
        try:
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory usage
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_available_gb = memory.available / (1024**3)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            disk_percent = (disk.used / disk.total) * 100
            disk_free_gb = disk.free / (1024**3)
            
            return {
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent,
                "memory_available_gb": round(memory_available_gb, 2),
                "disk_percent": round(disk_percent, 1),
                "disk_free_gb": round(disk_free_gb, 2)
            }
        except Exception as e:
            return {
                "error": str(e)
            }
    
    def _get_api_metrics(self):
        """Get API performance metrics"""
        try:
            avg_response_time = 0
            if self.response_times:
                avg_response_time = sum(self.response_times) / len(self.response_times)
            
            error_rate = 0
            if self.request_count > 0:
                error_rate = (self.error_count / self.request_count) * 100
            
            return {
                "total_requests": self.request_count,
                "total_errors": self.error_count,
                "error_rate_percent": round(error_rate, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "requests_per_minute": self._calculate_requests_per_minute()
            }
        except Exception as e:
            return {
                "error": str(e)
            }
    
    def _get_service_status(self):
        """Get status of individual services"""
        services = {}
        
        # Test data ingestion
        try:
            vehicle_count = Vehicle.query.count()
            services["data_ingestion"] = {
                "status": "active" if vehicle_count > 0 else "inactive",
                "vehicles_loaded": vehicle_count
            }
        except:
            services["data_ingestion"] = {"status": "error"}
        
        # Test vehicle matching
        try:
            match_count = VehicleMatch.query.count()
            services["vehicle_matching"] = {
                "status": "active" if match_count > 0 else "inactive",
                "total_matches": match_count
            }
        except:
            services["vehicle_matching"] = {"status": "error"}
        
        # Test pricing scoring
        try:
            score_count = VehicleScore.query.count()
            services["pricing_scoring"] = {
                "status": "active" if score_count > 0 else "inactive",
                "total_scores": score_count
            }
        except:
            services["pricing_scoring"] = {"status": "error"}
        
        # AI insights (always active since it's generated on-demand)
        services["ai_insights"] = {"status": "active"}
        
        return services
    
    def _calculate_requests_per_minute(self):
        """Calculate requests per minute based on uptime"""
        uptime_minutes = (datetime.now() - self.start_time).total_seconds() / 60
        if uptime_minutes > 0:
            return round(self.request_count / uptime_minutes, 2)
        return 0
    
    def _is_system_healthy(self, db_metrics, system_metrics, api_metrics):
        """Determine if system is healthy based on metrics"""
        try:
            # Check database connectivity
            if db_metrics.get("status") != "connected":
                return False
            
            # Check system resources
            if system_metrics.get("cpu_percent", 0) > 90:
                return False
            if system_metrics.get("memory_percent", 0) > 90:
                return False
            if system_metrics.get("disk_percent", 0) > 95:
                return False
            
            # Check API error rate
            if api_metrics.get("error_rate_percent", 0) > 10:
                return False
            
            return True
        except:
            return False
    
    def get_performance_summary(self):
        """Get a summary of key performance indicators"""
        try:
            health = self.get_system_health()
            
            return {
                "status": health["overall_status"],
                "uptime_hours": round(health["uptime_seconds"] / 3600, 1),
                "total_vehicles": health["database"]["total_vehicles"],
                "total_requests": health["api"]["total_requests"],
                "avg_response_time": health["api"]["avg_response_time_ms"],
                "error_rate": health["api"]["error_rate_percent"],
                "cpu_usage": health["system"]["cpu_percent"],
                "memory_usage": health["system"]["memory_percent"]
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }

# Global monitor instance
monitor = SystemMonitor()

def get_monitor():
    """Get the global monitor instance"""
    return monitor

