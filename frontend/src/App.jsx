import { useState } from 'react'
import { 
  Container, 
  Paper, 
  Typography, 
  Box,
  CircularProgress,
  CssBaseline,
  ThemeProvider,
  createTheme
} from '@mui/material'
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider'
import { AdapterDayjs } from '@mui/x-date-pickers/AdapterDayjs'
import { DatePicker } from '@mui/x-date-pickers/DatePicker'
import dayjs from 'dayjs'
import axios from 'axios'

// Configuration du thème
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
    },
    background: {
      default: '#f5f5f5',
    },
  },
});

function App() {
  const [date, setDate] = useState(dayjs())
  const [prediction, setPrediction] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleDateChange = async (newDate) => {
    setDate(newDate)
    setLoading(true)
    setError(null)
    
    try {
      const formattedDate = newDate.format('DD/MM/YYYY')
      const response = await axios.post('http://localhost:8000/predict', {
        date: formattedDate
      })
      
      setPrediction(response.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Une erreur est survenue')
    } finally {
      setLoading(false)
    }
  }

  const formatTraffic = (bits) => {
    if (bits >= 1000000) {
      return `${(bits / 1000000).toFixed(2)} Mb/s`
    } else if (bits >= 1000) {
      return `${(bits / 1000).toFixed(2)} kb/s`
    }
    return `${bits.toFixed(2)} b/s`
  }

  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <Box
        sx={{
          minHeight: '100vh',
          display: 'flex',
          alignItems: 'center',
          bgcolor: 'background.default',
        }}
      >
        <Container maxWidth="sm">
          <Paper 
            elevation={3} 
            sx={{ 
              p: 4,
              borderRadius: 2,
              bgcolor: 'white',
            }}
          >
            <Typography 
              variant="h4" 
              component="h1" 
              gutterBottom 
              align="center"
              sx={{ 
                color: 'primary.main',
                fontWeight: 'bold',
                mb: 4
              }}
            >
              Prédiction de Trafic Réseau
            </Typography>

            <Box sx={{ my: 4 }}>
              <DatePicker
                label="Sélectionnez une date"
                value={date}
                onChange={handleDateChange}
                format="DD/MM/YYYY"
                sx={{ 
                  width: '100%',
                  '& .MuiOutlinedInput-root': {
                    '&:hover fieldset': {
                      borderColor: 'primary.main',
                    },
                  },
                }}
              />
            </Box>

            <Box sx={{ mt: 4, textAlign: 'center' }}>
              {loading ? (
                <CircularProgress size={60} sx={{ color: 'primary.main' }} />
              ) : error ? (
                <Typography 
                  color="error" 
                  sx={{ 
                    bgcolor: '#ffebee',
                    p: 2,
                    borderRadius: 1
                  }}
                >
                  {error}
                </Typography>
              ) : prediction ? (
                <Box>
                  <Typography 
                    variant="h6" 
                    gutterBottom
                    sx={{ color: 'text.secondary' }}
                  >
                    Prédiction pour le {prediction.date}
                  </Typography>
                  <Typography 
                    variant="h4" 
                    sx={{ 
                      color: 'primary.main',
                      fontWeight: 'bold',
                      mt: 2
                    }}
                  >
                    {formatTraffic(prediction.predicted_traffic)}
                  </Typography>
                </Box>
              ) : null}
            </Box>
          </Paper>
        </Container>
      </Box>
    </ThemeProvider>
  )
}

export default App 