"""
Optimized database operations with improved performance and error handling.
"""

import os
import secrets
from typing import Optional, Tuple, List, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Table, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime
import bcrypt

from constants import DATABASE_CONFIG, VALIDATION_RULES, ERROR_MESSAGES

Base = declarative_base()

# Association table for user friendships
friendships = Table('friendships', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('friend_id', Integer, ForeignKey('users.id'), primary_key=True)
)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    weight_goal = Column(Float, nullable=True)
    preferred_language = Column(String(10), default='en')
    dark_mode = Column(Boolean, default=False)
    remember_token = Column(String(255), nullable=True)
    
    # Relationships
    activities = relationship("Activity", back_populates="user", cascade="all, delete-orphan")
    weight_entries = relationship("WeightEntry", back_populates="user", cascade="all, delete-orphan")
    
    # Friends relationship (many-to-many)
    friends = relationship(
        "User",
        secondary=friendships,
        primaryjoin=id == friendships.c.user_id,
        secondaryjoin=id == friendships.c.friend_id,
        back_populates="friends"
    )
    
    def set_password(self, password: str) -> None:
        """Hash and set password with validation."""
        if len(password) < VALIDATION_RULES['password_min_length']:
            raise ValueError(f"Password must be at least {VALIDATION_RULES['password_min_length']} characters")
        
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password: str) -> bool:
        """Check if provided password matches hash."""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
        except Exception:
            return False
    
    def generate_remember_token(self) -> str:
        """Generate a secure remember token."""
        self.remember_token = secrets.token_urlsafe(32)
        return self.remember_token
    
    def clear_remember_token(self) -> None:
        """Clear the remember token."""
        self.remember_token = None

class Activity(Base):
    __tablename__ = 'activities'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    type = Column(String(50), nullable=False)
    duration = Column(Integer, nullable=False)  # in minutes
    intensity = Column(String(20), nullable=False)
    date = Column(DateTime, nullable=False)
    description = Column(Text, nullable=True)
    adaptation = Column(String(100), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="activities")

class WeightEntry(Base):
    __tablename__ = 'weight_entries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    weight = Column(Float, nullable=False)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="weight_entries")


class OptimizedDatabaseManager:
    """
    Enhanced database manager with performance optimizations and better error handling.
    """
    
    def __init__(self):
        """Initialize with optimized configuration."""
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Fix postgres:// to postgresql:// for SQLAlchemy compatibility
        if self.database_url.startswith('postgres://'):
            self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)
        
        # Create optimized engine
        self.engine = create_engine(self.database_url, **DATABASE_CONFIG)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions with automatic cleanup."""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def create_user(self, username: str, email: str, password: str) -> Tuple[Optional[User], str]:
        """Create new user with validation and error handling."""
        try:
            # Validate input
            if len(username) < VALIDATION_RULES['username_min_length']:
                return None, f"Username must be at least {VALIDATION_RULES['username_min_length']} characters"
            
            if len(username) > VALIDATION_RULES['username_max_length']:
                return None, f"Username must be less than {VALIDATION_RULES['username_max_length']} characters"
            
            with self.get_session() as session:
                # Check if user already exists
                existing_user = session.query(User).filter(
                    (User.username == username) | (User.email == email)
                ).first()
                
                if existing_user:
                    if existing_user.username == username:
                        return None, "Username already exists"
                    else:
                        return None, "Email already exists"
                
                # Create new user
                user = User(username=username, email=email)
                user.set_password(password)
                
                session.add(user)
                session.flush()  # Get the ID without committing
                
                return user, "User created successfully"
                
        except ValueError as e:
            return None, str(e)
        except SQLAlchemyError as e:
            return None, f"Database error: {str(e)}"
        except Exception as e:
            return None, f"Unexpected error: {str(e)}"
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Authenticate user with optimized query and session management."""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.username == username).first()
                
                if user and user.check_password(password):
                    # Force load all attributes while session is active
                    _ = user.id, user.username, user.dark_mode, user.preferred_language
                    # Expunge from session to avoid DetachedInstanceError
                    session.expunge(user)
                    return user
                return None
                
        except SQLAlchemyError:
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID with error handling."""
        try:
            with self.get_session() as session:
                return session.query(User).filter(User.id == user_id).first()
        except SQLAlchemyError:
            return None
    
    def update_user_preferences(self, user_id: int, **preferences) -> bool:
        """Update user preferences with validation."""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return False
                
                # Update allowed preferences
                allowed_fields = ['preferred_language', 'dark_mode', 'weight_goal']
                for field, value in preferences.items():
                    if field in allowed_fields and hasattr(user, field):
                        setattr(user, field, value)
                
                return True
                
        except SQLAlchemyError:
            return False
    
    def set_remember_token(self, user_id: int, generate_token: bool = True) -> Optional[str]:
        """Set or clear remember token for user."""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return None
                
                if generate_token:
                    token = user.generate_remember_token()
                    return token
                else:
                    user.clear_remember_token()
                    return None
                    
        except SQLAlchemyError:
            return None
    
    def add_activity(self, user_id: int, activity_data: Dict[str, Any]) -> bool:
        """Add activity with validation."""
        try:
            # Validate required fields
            required_fields = ['type', 'duration', 'intensity', 'date']
            if not all(field in activity_data for field in required_fields):
                return False
            
            # Validate duration
            duration = activity_data['duration']
            if not (VALIDATION_RULES['min_duration'] <= duration <= VALIDATION_RULES['max_duration']):
                return False
            
            with self.get_session() as session:
                activity = Activity(
                    user_id=user_id,
                    type=activity_data['type'],
                    duration=activity_data['duration'],
                    intensity=activity_data['intensity'],
                    date=activity_data['date'],
                    description=activity_data.get('description', ''),
                    adaptation=activity_data.get('adaptation', '')
                )
                
                session.add(activity)
                return True
                
        except SQLAlchemyError:
            return False
    
    def get_user_activities(self, user_id: int, period: str = "All time", 
                           limit: int = None) -> List[Activity]:
        """Get user activities with optimized filtering."""
        try:
            with self.get_session() as session:
                query = session.query(Activity).filter(Activity.user_id == user_id)
                
                # Apply date filter based on period
                if period != "All time":
                    from datetime import timedelta
                    now = datetime.now()
                    if period == "Week":
                        cutoff_date = now - timedelta(days=7)
                    elif period == "Month":
                        cutoff_date = now - timedelta(days=30)
                    elif period == "Season":
                        cutoff_date = now - timedelta(days=90)
                    else:
                        cutoff_date = None
                    
                    if cutoff_date:
                        query = query.filter(Activity.date >= cutoff_date)
                
                # Order by date descending
                query = query.order_by(Activity.date.desc())
                
                # Apply limit if specified (default limit to prevent huge queries)
                query = query.limit(limit or 1000)
                
                return query.all()
                
        except SQLAlchemyError:
            return []
    
    def delete_activity(self, user_id: int, activity_id: int) -> bool:
        """Delete user's activity with authorization check."""
        try:
            with self.get_session() as session:
                activity = session.query(Activity).filter(
                    Activity.id == activity_id,
                    Activity.user_id == user_id
                ).first()
                
                if not activity:
                    return False
                
                session.delete(activity)
                return True
                
        except SQLAlchemyError:
            return False
    
    def add_weight_entry(self, user_id: int, weight: float, date: datetime) -> bool:
        """Add weight entry with validation."""
        try:
            # Validate weight
            if not (VALIDATION_RULES['min_weight'] <= weight <= VALIDATION_RULES['max_weight']):
                return False
            
            with self.get_session() as session:
                weight_entry = WeightEntry(
                    user_id=user_id,
                    weight=weight,
                    date=date
                )
                
                session.add(weight_entry)
                return True
                
        except SQLAlchemyError:
            return False
    
    def get_user_weight_entries(self, user_id: int, limit: int = None) -> List[WeightEntry]:
        """Get user weight entries ordered by date."""
        try:
            with self.get_session() as session:
                query = session.query(WeightEntry).filter(
                    WeightEntry.user_id == user_id
                ).order_by(WeightEntry.date.asc())
                
                if limit:
                    query = query.limit(limit)
                
                return query.all()
                
        except SQLAlchemyError:
            return []
    
    def delete_weight_entry(self, user_id: int, entry_id: int) -> bool:
        """Delete user's weight entry with authorization check."""
        try:
            with self.get_session() as session:
                entry = session.query(WeightEntry).filter(
                    WeightEntry.id == entry_id,
                    WeightEntry.user_id == user_id
                ).first()
                
                if not entry:
                    return False
                
                session.delete(entry)
                return True
                
        except SQLAlchemyError:
            return False
    
    def add_friend(self, user_id: int, friend_username: str) -> Tuple[bool, str]:
        """Add friend relationship with validation."""
        try:
            with self.get_session() as session:
                # Find friend by username
                friend = session.query(User).filter(User.username == friend_username).first()
                if not friend:
                    return False, "User not found"
                
                if friend.id == user_id:
                    return False, "Cannot add yourself as friend"
                
                # Check if friendship already exists
                user = session.query(User).filter(User.id == user_id).first()
                if not user:
                    return False, "User not found"
                
                if friend in user.friends:
                    return False, "Already friends"
                
                # Add bidirectional friendship
                user.friends.append(friend)
                friend.friends.append(user)
                
                return True, "Friend added successfully"
                
        except SQLAlchemyError as e:
            return False, f"Database error: {str(e)}"
    
    def get_user_friends(self, user_id: int) -> List[User]:
        """Get user's friends list."""
        try:
            with self.get_session() as session:
                user = session.query(User).filter(User.id == user_id).first()
                return user.friends if user else []
        except SQLAlchemyError:
            return []
    
    def get_friends_recent_activities(self, user_id: int, limit: int = 10) -> List[Activity]:
        """Get recent activities from user's friends."""
        try:
            with self.get_session() as session:
                # Get friend IDs
                user = session.query(User).filter(User.id == user_id).first()
                if not user or not user.friends:
                    return []
                
                friend_ids = [friend.id for friend in user.friends]
                
                # Get recent activities from friends
                activities = session.query(Activity).filter(
                    Activity.user_id.in_(friend_ids)
                ).order_by(Activity.date.desc()).limit(limit).all()
                
                return activities
                
        except SQLAlchemyError:
            return []
    
    def get_activity_statistics(self, user_id: int, period_days: int = 30) -> Dict[str, Any]:
        """Get activity statistics for user."""
        try:
            with self.get_session() as session:
                cutoff_date = datetime.now() - timedelta(days=period_days)
                
                # Get activity stats using efficient queries
                stats = session.query(
                    func.count(Activity.id).label('total_activities'),
                    func.sum(Activity.duration).label('total_duration'),
                    func.avg(Activity.duration).label('avg_duration')
                ).filter(
                    Activity.user_id == user_id,
                    Activity.date >= cutoff_date
                ).first()
                
                return {
                    'total_activities': stats.total_activities or 0,
                    'total_duration': stats.total_duration or 0,
                    'avg_duration': round(stats.avg_duration or 0, 1)
                }
                
        except SQLAlchemyError:
            return {'total_activities': 0, 'total_duration': 0, 'avg_duration': 0}
    
    def cleanup_old_tokens(self, days_old: int = 30) -> int:
        """Cleanup old remember tokens for security."""
        try:
            with self.get_session() as session:
                cutoff_date = datetime.now() - timedelta(days=days_old)
                
                # Clear tokens for users who haven't been active
                result = session.query(User).filter(
                    User.remember_token.isnot(None),
                    User.created_at < cutoff_date
                ).update({User.remember_token: None})
                
                return result
                
        except SQLAlchemyError:
            return 0


# Backward compatibility
class DatabaseManager(OptimizedDatabaseManager):
    """Backward compatibility wrapper."""
    
    def get_session(self):
        """Get session without context manager for backward compatibility."""
        return self.SessionLocal()
    
    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        """Backward compatible authentication."""
        return super().authenticate_user(username, password)
    
    def get_user_activities(self, user_id: int, period: str = "All time") -> List[Activity]:
        """Backward compatible activity retrieval."""
        return super().get_user_activities(user_id, period)