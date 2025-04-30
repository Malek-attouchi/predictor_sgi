import { useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Box,
  CircularProgress,
  CssBaseline,
  ThemeProvider,
  createTheme,
  TextField,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Card,
  CardContent,
  Grid,
  Fade,
  Zoom,
  Tabs,
  Tab,
  AppBar,
  Toolbar,
  IconButton,
  useMediaQuery,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Chip,
  Avatar,
  Tooltip,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Timeline as TimelineIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import dayjs, { Dayjs } from 'dayjs';
import axios from 'axios';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip as ChartTooltip,
  Legend,
} from 'chart.js';

// Enregistrement des composants Chart.js
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  ChartTooltip,
  Legend
);

const theme = createTheme({
  palette: {
    primary: {
      main: '#3f51b5',
      light: '#757de8',
      dark: '#002984',
    },
    secondary: {
      main: '#f50057',
      light: '#ff4081',
      dark: '#c51162',
    },
    background: {
      default: '#f5f5f5',
      paper: '#ffffff',
    },
    success: {
      main: '#4caf50',
      light: '#81c784',
      dark: '#388e3c',
    },
  },
  typography: {
    fontFamily: '"Poppins", "Roboto", "Helvetica", "Arial", sans-serif',
    h4: {
      fontWeight: 600,
      letterSpacing: '0.5px',
    },
    h6: {
      fontWeight: 500,
    },
    body1: {
      fontSize: '1rem',
    },
  },
  components: {
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 8,
          textTransform: 'none',
          padding: '8px 16px',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-2px)',
            boxShadow: '0 4px 8px rgba(0,0,0,0.1)',
          },
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 8px 16px rgba(0, 0, 0, 0.1)',
        },
      },
    },
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 16,
          boxShadow: '0 4px 8px rgba(0, 0, 0, 0.05)',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: '0 8px 16px rgba(0, 0, 0, 0.1)',
          },
        },
      },
    },
    MuiAppBar: {
      styleOverrides: {
        root: {
          borderRadius: 0,
          boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
        },
      },
    },
  },
});

function App() {
  const [date, setDate] = useState<Dayjs | null>(dayjs());
  const [predictionType, setPredictionType] = useState<string>('single');
  const [prediction, setPrediction] = useState<any>(null);
  const [dailyPredictions, setDailyPredictions] = useState<any[]>([]);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [trafficData, setTrafficData] = useState<any[]>([]);
  const [loadingTrafficData, setLoadingTrafficData] = useState<boolean>(false);
  const [activeTab, setActiveTab] = useState(0);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleDateChange = (newDate: Dayjs | null) => {
    setDate(newDate);
  };

  const handlePredictionTypeChange = (event: any) => {
    setPredictionType(event.target.value);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const toggleDrawer = () => {
    setDrawerOpen(!drawerOpen);
  };

  const handlePredict = async () => {
    if (!date) {
      setError('Veuillez sélectionner une date.');
      return;
    }

    setLoading(true);
    setError(null);
    setPrediction(null);
    setDailyPredictions([]);

    try {
      const formattedDate = date.format('DD/MM/YYYY HH:mm');
      const endpoint = predictionType === 'single' ? '/predict' : '/predict_day';
      const response = await axios.post(`http://localhost:5000${endpoint}`, {
        date: formattedDate,
      });

      if (predictionType === 'single') {
        setPrediction(response.data);
      } else {
        setDailyPredictions(response.data);
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Une erreur est survenue');
    } finally {
      setLoading(false);
    }
  };

  const handleLoadTrafficData = async () => {
    setLoadingTrafficData(true);
    setError(null);
    try {
      const response = await axios.get('http://localhost:5000/traffic_data');
      setTrafficData(response.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Une erreur est survenue lors du chargement des données.');
    } finally {
      setLoadingTrafficData(false);
    }
  };

  const formatTraffic = (bits: number) => {
    if (bits >= 1000000) {
      return `${(bits / 1000000).toFixed(2)} Mb/s`;
    } else if (bits >= 1000) {
      return `${(bits / 1000).toFixed(2)} kb/s`;
    }
    return `${bits.toFixed(2)} b/s`;
  };

  const chartData = {
    labels: dailyPredictions.map((p) => p.date),
    datasets: [
      {
        label: 'Trafic prédit',
        data: dailyPredictions.map((p) => p.predicted_traffic),
        borderColor: theme.palette.primary.main,
        backgroundColor: theme.palette.primary.light + '40',
        tension: 0.4,
        fill: true,
        pointRadius: 4,
        pointHoverRadius: 6,
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    plugins: {
      legend: {
        position: 'top' as const,
      },
      title: {
        display: true,
        text: 'Prédictions de trafic journalières',
        font: {
          size: 16,
          weight: 'bold',
        },
      },
      tooltip: {
        backgroundColor: 'rgba(0, 0, 0, 0.8)',
        titleFont: {
          size: 14,
          weight: 'bold',
        },
        bodyFont: {
          size: 12,
        },
        padding: 10,
        cornerRadius: 8,
      },
    },
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: 'Trafic (bits/s)',
          font: {
            weight: 'bold',
          },
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
      x: {
        title: {
          display: true,
          text: 'Heure',
          font: {
            weight: 'bold',
          },
        },
        grid: {
          color: 'rgba(0, 0, 0, 0.05)',
        },
      },
    },
  };

  const drawer = (
    <Box sx={{ width: 250 }}>
      <Toolbar />
      <Divider />
      <List>
        <ListItem button>
          <ListItemIcon>
            <TimelineIcon color="primary" />
          </ListItemIcon>
          <ListItemText primary="Prédictions" />
        </ListItem>
        <ListItem button>
          <ListItemIcon>
            <HistoryIcon color="primary" />
          </ListItemIcon>
          <ListItemText primary="Historique" />
        </ListItem>
        <ListItem button>
          <ListItemIcon>
            <SettingsIcon color="primary" />
          </ListItemIcon>
          <ListItemText primary="Paramètres" />
        </ListItem>
      </List>
    </Box>
  );

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box sx={{ display: 'flex', minHeight: '100vh' }}>
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }}>
          <Toolbar>
            <IconButton
              color="inherit"
              edge="start"
              onClick={toggleDrawer}
              sx={{ mr: 2 }}
            >
              <MenuIcon />
            </IconButton>
            <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
              Traffic Predictor
            </Typography>
            <Tooltip title="Actualiser les données">
              <IconButton color="inherit" onClick={handleLoadTrafficData}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="À propos">
              <IconButton color="inherit">
                <InfoIcon />
              </IconButton>
            </Tooltip>
          </Toolbar>
        </AppBar>

        <Drawer
          variant={isMobile ? "temporary" : "permanent"}
          open={drawerOpen}
          onClose={toggleDrawer}
          sx={{
            width: 250,
            flexShrink: 0,
            '& .MuiDrawer-paper': {
              width: 250,
              boxSizing: 'border-box',
            },
          }}
        >
          {drawer}
        </Drawer>

        <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
          <Container maxWidth="lg">
            <Fade in timeout={500}>
              <Paper
                elevation={3}
                sx={{
                  p: 4,
                  borderRadius: 2,
                  bgcolor: 'background.paper',
                }}
              >
                <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
                  <Tabs value={activeTab} onChange={handleTabChange}>
                    <Tab label="Prédiction" />
                    <Tab label="Historique" />
                    <Tab label="Statistiques" />
                  </Tabs>
                </Box>

                {activeTab === 0 && (
                  <Grid container spacing={3}>
                    <Grid item xs={12} md={6}>
                      <Card>
                        <CardContent>
                          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                            <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                              <TimelineIcon />
                            </Avatar>
                            <Typography variant="h6">
                              Configuration de la prédiction
                            </Typography>
                          </Box>
                          <FormControl fullWidth sx={{ mb: 2 }}>
                            <InputLabel>Type de prédiction</InputLabel>
                            <Select
                              value={predictionType}
                              onChange={handlePredictionTypeChange}
                              label="Type de prédiction"
                            >
                              <MenuItem value="single">Prédiction unique</MenuItem>
                              <MenuItem value="daily">Prédiction journalière</MenuItem>
                            </Select>
                          </FormControl>

                          <LocalizationProvider dateAdapter={AdapterDayjs}>
                            <DateTimePicker
                              label="Sélectionnez une date et heure"
                              value={date}
                              onChange={handleDateChange}
                              format="DD/MM/YYYY HH:mm"
                              sx={{
                                width: '100%',
                                '& .MuiOutlinedInput-root': {
                                  '&:hover fieldset': {
                                    borderColor: 'primary.main',
                                  },
                                },
                              }}
                            />
                          </LocalizationProvider>

                          <Button
                            variant="contained"
                            color="primary"
                            onClick={handlePredict}
                            disabled={loading}
                            sx={{ mt: 2, width: '100%' }}
                            startIcon={loading ? <CircularProgress size={20} /> : null}
                          >
                            {loading ? 'Prédiction en cours...' : 'Lancer la prédiction'}
                          </Button>
                        </CardContent>
                      </Card>
                    </Grid>

                    <Grid item xs={12} md={6}>
                      {error && (
                        <Zoom in>
                          <Card sx={{ mb: 3, bgcolor: 'error.light' }}>
                            <CardContent>
                              <Typography color="error">
                                {error}
                              </Typography>
                            </CardContent>
                          </Card>
                        </Zoom>
                      )}

                      {prediction && (
                        <Zoom in>
                          <Card>
                            <CardContent>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Avatar sx={{ bgcolor: 'success.main', mr: 2 }}>
                                  <TimelineIcon />
                                </Avatar>
                                <Typography variant="h6">
                                  Résultat de la prédiction
                                </Typography>
                              </Box>
                              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                                <Typography>
                                  <strong>Date :</strong> {prediction.date}
                                </Typography>
                                <Typography>
                                  <strong>Trafic prédit :</strong> {formatTraffic(prediction.predicted_traffic)}
                                </Typography>
                                <Chip
                                  label="Prédiction unique"
                                  color="primary"
                                  sx={{ mt: 2, alignSelf: 'flex-start' }}
                                />
                              </Box>
                            </CardContent>
                          </Card>
                        </Zoom>
                      )}

                      {dailyPredictions.length > 0 && (
                        <Zoom in>
                          <Card>
                            <CardContent>
                              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                                <Avatar sx={{ bgcolor: 'secondary.main', mr: 2 }}>
                                  <TimelineIcon />
                                </Avatar>
                                <Typography variant="h6">
                                  Prédictions journalières
                                </Typography>
                              </Box>
                              <Box sx={{ height: 300, mb: 4 }}>
                                <Line data={chartData} options={chartOptions} />
                              </Box>
                              <TableContainer>
                                <Table>
                                  <TableHead>
                                    <TableRow>
                                      <TableCell>Date</TableCell>
                                      <TableCell>Trafic prédit</TableCell>
                                    </TableRow>
                                  </TableHead>
                                  <TableBody>
                                    {dailyPredictions.map((p, index) => (
                                      <TableRow key={index}>
                                        <TableCell>{p.date}</TableCell>
                                        <TableCell>{formatTraffic(p.predicted_traffic)}</TableCell>
                                      </TableRow>
                                    ))}
                                  </TableBody>
                                </Table>
                              </TableContainer>
                            </CardContent>
                          </Card>
                        </Zoom>
                      )}
                    </Grid>
                  </Grid>
                )}

                {activeTab === 1 && (
                  <Zoom in>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                            <HistoryIcon />
                          </Avatar>
                          <Typography variant="h6">
                            Historique des données
                          </Typography>
                        </Box>
                        <Button
                          variant="outlined"
                          color="secondary"
                          onClick={handleLoadTrafficData}
                          disabled={loadingTrafficData}
                          sx={{ mb: 2 }}
                          startIcon={loadingTrafficData ? <CircularProgress size={20} /> : <RefreshIcon />}
                        >
                          {loadingTrafficData ? 'Chargement...' : 'Actualiser les données'}
                        </Button>
                        <TableContainer>
                          <Table>
                            <TableHead>
                              <TableRow>
                                <TableCell>Timestamp</TableCell>
                                <TableCell>Valeur</TableCell>
                                <TableCell>Source</TableCell>
                              </TableRow>
                            </TableHead>
                            <TableBody>
                              {trafficData.map((data, index) => (
                                <TableRow key={index}>
                                  <TableCell>{data.timestamp}</TableCell>
                                  <TableCell>{formatTraffic(data.value)}</TableCell>
                                  <TableCell>
                                    <Chip
                                      label={data.source}
                                      color={data.source === 'capture' ? 'primary' : 'secondary'}
                                      size="small"
                                    />
                                  </TableCell>
                                </TableRow>
                              ))}
                            </TableBody>
                          </Table>
                        </TableContainer>
                      </CardContent>
                    </Card>
                  </Zoom>
                )}

                {activeTab === 2 && (
                  <Zoom in>
                    <Card>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                          <Avatar sx={{ bgcolor: 'primary.main', mr: 2 }}>
                            <TimelineIcon />
                          </Avatar>
                          <Typography variant="h6">
                            Statistiques
                          </Typography>
                        </Box>
                        <Grid container spacing={3}>
                          <Grid item xs={12} md={4}>
                            <Card sx={{ bgcolor: 'primary.light', color: 'white' }}>
                              <CardContent>
                                <Typography variant="h6">Total des données</Typography>
                                <Typography variant="h4">{trafficData.length}</Typography>
                              </CardContent>
                            </Card>
                          </Grid>
                          <Grid item xs={12} md={4}>
                            <Card sx={{ bgcolor: 'secondary.light', color: 'white' }}>
                              <CardContent>
                                <Typography variant="h6">Prédictions</Typography>
                                <Typography variant="h4">{dailyPredictions.length}</Typography>
                              </CardContent>
                            </Card>
                          </Grid>
                          <Grid item xs={12} md={4}>
                            <Card sx={{ bgcolor: 'success.light', color: 'white' }}>
                              <CardContent>
                                <Typography variant="h6">Précision</Typography>
                                <Typography variant="h4">95%</Typography>
                              </CardContent>
                            </Card>
                          </Grid>
                        </Grid>
                      </CardContent>
                    </Card>
                  </Zoom>
                )}
              </Paper>
            </Fade>
          </Container>
        </Box>
      </Box>
    </ThemeProvider>
  );
}

export default App;
