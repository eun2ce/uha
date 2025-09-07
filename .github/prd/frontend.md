# UHA Frontend Development Context

## 🎨 UI/UX Design System

### Design Philosophy: Toss-Inspired Mobile-First
- **Mobile-First**: 최대 430px (iPhone 14 Pro Max) 반응형
- **Modern Typography**: 800 weight headers, optimized letter-spacing
- **Subtle Animations**: Scale, fade, slide transitions
- **Card-Based Layout**: 20px border radius, layered shadows
- **Color Psychology**: Brand colors with semantic meaning

### Color Palette
```typescript
const colors = {
  // Primary brand colors
  indigo: '#4F46E5',      // Live Streams
  emerald: '#059669',     // AI Summary  
  naver: '#00C73C',       // Naver Cafe
  
  // Neutral palette
  background: '#FAFAFA',   // App background
  surface: '#FFFFFF',     // Card background
  border: '#E5E7EB',      // Subtle borders
  text: {
    primary: '#111827',   // Headers
    secondary: '#6B7280', // Body text
    muted: '#9CA3AF'      // Captions
  }
}
```

### Typography Scale
```typescript
const typography = {
  // Headers
  h1: { fontSize: 28, fontWeight: '800', letterSpacing: -0.5 },
  h2: { fontSize: 18, fontWeight: '700', letterSpacing: -0.2 },
  
  // Body text
  body: { fontSize: 14, fontWeight: '500', lineHeight: 20 },
  caption: { fontSize: 12, fontWeight: '600' },
  
  // Interactive elements
  button: { fontSize: 14, fontWeight: '700' },
  tab: { fontSize: 12, fontWeight: '600' }
}
```

## 📱 Component Architecture

### Core Components Structure
```
screens/
├── MainScreen.tsx           # Root container with tab navigation
├── youtube/
│   └── components/
│       ├── StreamList.tsx   # Paginated stream list
│       ├── StreamCard.tsx   # Individual stream card
│       ├── SummarySection.tsx # AI summary display
│       └── Pagination.tsx   # Page navigation
├── naver/
│   └── NaverCafeScreen.tsx  # Naver Cafe content
└── common/
    └── Header.tsx           # Shared header component
```

### Component Design Patterns

#### StreamCard Component
```typescript
interface StreamData {
  date: string;
  url: string;
  video_id: string;
  title?: string;
  thumbnail?: string;
  view_count?: number;
  like_count?: number;
  comment_count?: number;
  duration?: string;
  tags?: string[];
  keywords?: string[];
  ai_summary?: string;
  highlights?: string[];
  sentiment?: string;
  engagement_score?: number;
  category?: string;
}
```

#### Animation Patterns
```typescript
// Card press animation
const scaleAnim = new Animated.Value(1);

const handlePressIn = () => {
  Animated.spring(scaleAnim, {
    toValue: 0.98,
    useNativeDriver: true,
  }).start();
};

// Tab transition animation
const fadeAnim = new Animated.Value(1);
const slideAnim = new Animated.Value(0);

useEffect(() => {
  Animated.parallel([
    Animated.timing(fadeAnim, { toValue: 0, duration: 150 }),
    Animated.timing(slideAnim, { toValue: -20, duration: 150 })
  ]).start(() => {
    // Content change
    Animated.parallel([
      Animated.timing(fadeAnim, { toValue: 1, duration: 200 }),
      Animated.timing(slideAnim, { toValue: 0, duration: 200 })
    ]).start();
  });
}, [activeTab]);
```

## 🚀 Technology Stack

### Core Framework
- **React Native Web**: Cross-platform compatibility
- **TypeScript**: Type safety and developer experience
- **React Navigation**: Tab-based navigation
- **Animated API**: Native performance animations

### State Management
```typescript
// Local state with hooks
const [activeTab, setActiveTab] = useState<TabType>('streams');
const [currentYear, setCurrentYear] = useState(2025);
const [streams, setStreams] = useState<StreamData[]>([]);
const [loading, setLoading] = useState(false);

// Future: Context API for global state
interface AppContextType {
  user: User | null;
  settings: AppSettings;
  cache: CacheState;
}
```

### API Integration
```typescript
// Backend communication
const API_BASE_URL = 'http://localhost:8000';

const fetchStreams = async (year: number, page: number = 1) => {
  const response = await fetch(`${API_BASE_URL}/llm/streams`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      year,
      page,
      per_page: 10,
      include_details: true
    })
  });
  return response.json();
};
```

## 🎯 Key Features Implementation

### 1. Mobile-Responsive Layout
```typescript
// App.tsx - Mobile container
const { width } = Dimensions.get('window');

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
    justifyContent: 'center',
    alignItems: 'center',
  },
  mobileContainer: {
    width: Math.min(width, 430), // Max iPhone 14 Pro Max width
    height: '100%',
    backgroundColor: '#ffffff',
    borderRadius: width > 430 ? 16 : 0,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.1,
    shadowRadius: 12,
    elevation: 8,
  },
});
```

### 2. Interactive Tab Navigation
```typescript
// MainScreen.tsx - Tab system
const tabs = [
  { id: 'streams', title: '라이브 스트림', icon: '📺', color: '#4F46E5' },
  { id: 'summary', title: 'AI 요약', icon: '🤖', color: '#059669' },
  { id: 'naver', title: '네이버 카페', icon: '🟢', color: '#00C73C' },
];

const getCurrentTab = () => tabs.find(tab => tab.id === activeTab);
```

### 3. Stream Card Design
```typescript
// StreamCard.tsx - Card styling
const styles = StyleSheet.create({
  cardContainer: {
    marginHorizontal: 20,
    marginBottom: 16,
  },
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.08,
    shadowRadius: 12,
    elevation: 6,
    overflow: 'hidden',
    borderWidth: 0.5,
    borderColor: '#F3F4F6',
  },
  thumbnailContainer: {
    position: 'relative',
    height: 200,
    backgroundColor: '#F9FAFB',
  },
  content: {
    padding: 20,
  }
});
```

### 4. Data Formatting Utils
```typescript
// Utility functions for data display
const formatNumber = (num?: number): string => {
  if (!num) return '0';
  if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
  if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
  return num.toString();
};

const formatDate = (dateStr: string): string => {
  try {
    const date = new Date(dateStr);
    return date.toLocaleDateString('ko-KR', {
      month: 'short',
      day: 'numeric',
      weekday: 'short'
    });
  } catch {
    return dateStr;
  }
};

const formatDuration = (duration?: string): string => {
  if (!duration) return '';
  // Parse ISO 8601 duration (PT1H30M45S)
  const match = duration.match(/PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?/);
  if (!match) return duration;
  
  const hours = parseInt(match[1] || '0');
  const minutes = parseInt(match[2] || '0');
  const seconds = parseInt(match[3] || '0');
  
  if (hours > 0) {
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  }
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
};
```

## 🔄 State Management Patterns

### Current Implementation (Local State)
```typescript
// StreamList.tsx
const [streams, setStreams] = useState<StreamData[]>([]);
const [loading, setLoading] = useState(false);
const [refreshing, setRefreshing] = useState(false);
const [currentPage, setCurrentPage] = useState(1);
const [totalPages, setTotalPages] = useState(1);
const [error, setError] = useState<string | null>(null);
```

### Future Enhancement (Context API)
```typescript
// contexts/AppContext.tsx
interface AppState {
  streams: {
    [year: number]: {
      data: StreamData[];
      currentPage: number;
      totalPages: number;
      lastFetch: Date;
    }
  };
  cache: {
    enabled: boolean;
    stats: CacheStats;
  };
  ui: {
    activeTab: TabType;
    currentYear: number;
    theme: 'light' | 'dark';
  };
}

const AppContext = createContext<AppState | null>(null);
```

## 🎨 Animation System

### Micro-Interactions
```typescript
// Touch feedback animations
const AnimatedTouchable = ({ children, onPress, style }) => {
  const scaleAnim = useRef(new Animated.Value(1)).current;
  
  const handlePressIn = () => {
    Animated.spring(scaleAnim, {
      toValue: 0.98,
      useNativeDriver: true,
    }).start();
  };
  
  const handlePressOut = () => {
    Animated.spring(scaleAnim, {
      toValue: 1,
      useNativeDriver: true,
    }).start();
  };
  
  return (
    <Animated.View style={[style, { transform: [{ scale: scaleAnim }] }]}>
      <TouchableOpacity
        onPressIn={handlePressIn}
        onPressOut={handlePressOut}
        onPress={onPress}
        activeOpacity={1}
      >
        {children}
      </TouchableOpacity>
    </Animated.View>
  );
};
```

### Page Transitions
```typescript
// Tab content animation
const ContentWrapper = ({ children, activeTab }) => {
  const fadeAnim = useRef(new Animated.Value(1)).current;
  const slideAnim = useRef(new Animated.Value(0)).current;
  
  useEffect(() => {
    Animated.sequence([
      Animated.parallel([
        Animated.timing(fadeAnim, { toValue: 0, duration: 150 }),
        Animated.timing(slideAnim, { toValue: -20, duration: 150 })
      ]),
      Animated.parallel([
        Animated.timing(fadeAnim, { toValue: 1, duration: 200 }),
        Animated.timing(slideAnim, { toValue: 0, duration: 200 })
      ])
    ]).start();
  }, [activeTab]);
  
  return (
    <Animated.View style={{
      opacity: fadeAnim,
      transform: [{ translateY: slideAnim }]
    }}>
      {children}
    </Animated.View>
  );
};
```

## 🚀 Development Workflow

### Environment Setup
```bash
# Install dependencies
cd uha/projects/uha-frontend
npm install

# Start development server
npm start

# Available scripts
npm run web         # Web development
npm run ios         # iOS simulator
npm run android     # Android emulator
```

### Project Structure
```
uha-frontend/
├── App.tsx                 # Root component
├── package.json           # Dependencies
├── tsconfig.json          # TypeScript config
├── screens/               # Screen components
├── components/            # Shared components
├── assets/               # Images, icons
├── utils/                # Helper functions
└── types/                # TypeScript definitions
```

## 🧪 Testing Strategy

### Manual Testing Checklist
- [ ] **Responsive Design**: Test on different screen sizes
- [ ] **Touch Interactions**: Verify all animations work
- [ ] **API Integration**: Check data loading states
- [ ] **Error Handling**: Test network failures
- [ ] **Performance**: Monitor scroll performance

### Future Testing Framework
```typescript
// Jest + React Native Testing Library
import { render, fireEvent, waitFor } from '@testing-library/react-native';
import StreamCard from '../components/StreamCard';

test('StreamCard displays stream information', async () => {
  const mockStream = {
    title: 'Test Stream',
    thumbnail: 'https://example.com/thumb.jpg',
    view_count: 1500,
  };
  
  const { getByText } = render(<StreamCard stream={mockStream} />);
  
  expect(getByText('Test Stream')).toBeTruthy();
  expect(getByText('1.5K')).toBeTruthy();
});
```

## 🔮 Future Enhancements

### Performance Optimizations
- **React.memo**: Prevent unnecessary re-renders
- **useMemo/useCallback**: Optimize expensive computations
- **FlatList**: Virtualized scrolling for large lists
- **Image Caching**: Optimize thumbnail loading

### User Experience
- **Dark Mode**: Theme switching capability
- **Offline Support**: Cache data for offline viewing
- **Push Notifications**: New stream alerts
- **Search & Filter**: Advanced stream discovery

### Accessibility
- **Screen Reader**: VoiceOver/TalkBack support
- **High Contrast**: Accessibility color themes
- **Font Scaling**: Dynamic type support
- **Keyboard Navigation**: Full keyboard accessibility

### Advanced Features
- **Infinite Scroll**: Seamless pagination
- **Pull-to-Refresh**: Native refresh gestures
- **Share Integration**: Native sharing capabilities
- **Deep Linking**: URL-based navigation

## 📊 Performance Monitoring

### Key Metrics
- **First Paint**: < 1 second
- **Interactive**: < 2 seconds
- **Smooth Animations**: 60 FPS
- **Memory Usage**: < 100MB

### Monitoring Tools
```typescript
// Performance measurement
import { performance } from 'perf_hooks';

const measureRenderTime = (componentName: string) => {
  const start = performance.now();
  
  return () => {
    const end = performance.now();
    console.log(`${componentName} render time: ${end - start}ms`);
  };
};

// Usage in component
const StreamCard = ({ stream }) => {
  const endMeasure = measureRenderTime('StreamCard');
  
  useEffect(() => {
    endMeasure();
  });
  
  return <View>...</View>;
};
```

## 🐛 Common Issues & Solutions

### Layout Issues
```typescript
// Fix: Ensure consistent spacing
const styles = StyleSheet.create({
  container: {
    paddingHorizontal: 20, // Consistent horizontal padding
    paddingVertical: 16,   // Consistent vertical padding
  }
});
```

### Animation Performance
```typescript
// Fix: Always use useNativeDriver when possible
Animated.timing(value, {
  toValue: 1,
  duration: 200,
  useNativeDriver: true, // Offload to native thread
}).start();
```

### Memory Leaks
```typescript
// Fix: Cleanup animations in useEffect
useEffect(() => {
  const animation = Animated.timing(value, { ... });
  animation.start();
  
  return () => {
    animation.stop(); // Cleanup on unmount
  };
}, []);
```

### API Error Handling
```typescript
// Robust error handling
const fetchWithRetry = async (url: string, retries = 3) => {
  for (let i = 0; i < retries; i++) {
    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      if (i === retries - 1) throw error;
      await new Promise(resolve => setTimeout(resolve, 1000 * (i + 1)));
    }
  }
};
```

## 📱 Platform Considerations

### Web Deployment
```bash
# Build for web
npm run web

# Deploy to static hosting
npm run build
# Upload dist/ folder to hosting service
```

### Mobile Deployment
```bash
# iOS
npm run ios
# Requires Xcode and iOS Simulator

# Android  
npm run android
# Requires Android Studio and emulator
```

### Cross-Platform Compatibility
```typescript
// Platform-specific code
import { Platform } from 'react-native';

const styles = StyleSheet.create({
  shadow: Platform.select({
    ios: {
      shadowColor: '#000',
      shadowOffset: { width: 0, height: 2 },
      shadowOpacity: 0.1,
      shadowRadius: 4,
    },
    android: {
      elevation: 4,
    },
    web: {
      boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
    }
  }),
});
```

updated: 2025-09-07