"""Database setup and models for the fitness tracker app"""

import os
import secrets
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import bcrypt

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
    remember_token = Column(String(255), nullable=True)  # For remember me functionality
    
    # Relationships
    activities = relationship("Activity", back_populates="user")
    weight_entries = relationship("WeightEntry", back_populates="user")
    
    # Friends relationship (many-to-many)
    friends = relationship(
        "User",
        secondary=friendships,
        primaryjoin=id == friendships.c.user_id,
        secondaryjoin=id == friendships.c.friend_id,
        back_populates="friends"
    )
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def generate_remember_token(self):
        """Generate a secure remember token"""
        self.remember_token = secrets.token_urlsafe(32)
        return self.remember_token
    
    def clear_remember_token(self):
        """Clear the remember token"""
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

class DatabaseManager:
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        
        # Fix postgres:// to postgresql:// for SQLAlchemy compatibility
        if self.database_url.startswith('postgres://'):
            self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)
        
        # Optimize engine with connection pooling and performance settings
        from constants import DATABASE_CONFIG
        self.engine = create_engine(
            self.database_url,
            **DATABASE_CONFIG
        )
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        Base.metadata.create_all(bind=self.engine)
    
    def get_session(self):
        """Get database session"""
        return self.SessionLocal()
    
    def create_user(self, username, email, password):
        """Create new user"""
        session = self.get_session()
        try:
            # Check if user already exists
            existing_user = session.query(User).filter(
                (User.username == username) | (User.email == email)
            ).first()
            
            if existing_user:
                return None, "Username or email already exists"
            
            # Create new user
            user = User(username=username, email=email)
            user.set_password(password)
            
            session.add(user)
            session.commit()
            session.refresh(user)
            return user, "User created successfully"
            
        except Exception as e:
            session.rollback()
            return None, f"Error creating user: {str(e)}"
        finally:
            session.close()
    
    def authenticate_user(self, username, password):
        """Authenticate user with session management fix"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.username == username).first()
            if user and user.check_password(password):
                # Force load all attributes while session is active
                _ = user.id, user.username, user.dark_mode, user.preferred_language
                # Expunge from session to avoid DetachedInstanceError
                session.expunge(user)
                return user
            return None
        except Exception:
            return None
        finally:
            session.close()
    
    def set_remember_token(self, user_id, generate_token=True):
        """Set or clear remember token for user"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                if generate_token:
                    token = user.generate_remember_token()
                else:
                    user.clear_remember_token()
                    token = None
                session.commit()
                return token
            return None
        except Exception:
            return None
        finally:
            session.close()
    
    def authenticate_by_token(self, username, token):
        """Authenticate user by remember token"""
        session = self.get_session()
        try:
            user = session.query(User).filter(
                User.username == username,
                User.remember_token == token
            ).first()
            return user
        except Exception:
            return None
        finally:
            session.close()
    
    def add_friend(self, user_id, friend_username):
        """Add friend by username"""
        session = self.get_session()
        try:
            friend = session.query(User).filter(User.username == friend_username).first()
            if not friend:
                return False, "User not found"
            
            user = session.query(User).filter(User.id == user_id).first()
            if user and friend in user.friends:
                return False, "Already friends"
            
            if user:
                user.friends.append(friend)
            session.commit()
            return True, "Friend added successfully"
            
        except Exception as e:
            session.rollback()
            return False, f"Error adding friend: {str(e)}"
        finally:
            session.close()
    
    def get_user_activities(self, user_id, period="All time"):
        """Get user activities for period with optimized query"""
        session = self.get_session()
        try:
            query = session.query(Activity).filter(Activity.user_id == user_id)
            
            if period != "All time":
                from datetime import timedelta
                now = datetime.now()
                start_date = None
                if period == "Week":
                    start_date = now - timedelta(days=7)
                elif period == "Month":
                    start_date = now - timedelta(days=30)
                elif period == "Season":
                    start_date = now - timedelta(days=90)
                
                if start_date:
                    query = query.filter(Activity.date >= start_date)
            
            # Add limit to prevent loading too many records at once
            activities = query.order_by(Activity.date.desc()).limit(1000).all()
            return activities
            
        except Exception:
            return []
        finally:
            session.close()
    
    def add_activity(self, user_id, activity_data):
        """Add new activity"""
        session = self.get_session()
        try:
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
            session.commit()
            return True
            
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def delete_activity(self, user_id, activity_id):
        """Delete activity by ID for specific user"""
        session = self.get_session()
        try:
            activity = session.query(Activity).filter(
                Activity.id == activity_id,
                Activity.user_id == user_id
            ).first()
            
            if activity:
                session.delete(activity)
                session.commit()
                return True
            return False
            
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def update_activity(self, user_id, activity_id, activity_data):
        """Update existing activity"""
        session = self.get_session()
        try:
            activity = session.query(Activity).filter(
                Activity.id == activity_id,
                Activity.user_id == user_id
            ).first()
            
            if activity:
                activity.type = activity_data['type']
                activity.duration = activity_data['duration']
                activity.intensity = activity_data['intensity']
                activity.date = activity_data['date']
                activity.description = activity_data.get('description', '')
                activity.adaptation = activity_data.get('adaptation', '')
                
                session.commit()
                return True
            return False
            
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def get_user_weight_data(self, user_id):
        """Get user weight entries, sorted by date ascending (oldest first)"""
        session = self.get_session()
        try:
            entries = session.query(WeightEntry).filter(
                WeightEntry.user_id == user_id
            ).order_by(WeightEntry.date.asc()).all()
            return entries
        except Exception:
            return []
        finally:
            session.close()
    
    def add_weight_entry(self, user_id, weight, date):
        """Add weight entry"""
        session = self.get_session()
        try:
            entry = WeightEntry(user_id=user_id, weight=weight, date=date)
            session.add(entry)
            session.commit()
            return True
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def update_weight_entry(self, entry_id, weight, date):
        """Update weight entry"""
        session = self.get_session()
        try:
            entry = session.query(WeightEntry).filter(
                WeightEntry.id == entry_id
            ).first()
            
            if entry:
                entry.weight = weight
                entry.date = date
                session.commit()
                return True
            return False
            
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def delete_weight_entry(self, entry_id):
        """Delete weight entry"""
        session = self.get_session()
        try:
            entry = session.query(WeightEntry).filter(
                WeightEntry.id == entry_id
            ).first()
            
            if entry:
                session.delete(entry)
                session.commit()
                return True
            return False
            
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()
    
    def update_user_preferences(self, user_id, **preferences):
        """Update user preferences"""
        session = self.get_session()
        try:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                for key, value in preferences.items():
                    if hasattr(user, key):
                        setattr(user, key, value)
                session.commit()
                return True
            return False
        except Exception:
            session.rollback()
            return False
        finally:
            session.close()