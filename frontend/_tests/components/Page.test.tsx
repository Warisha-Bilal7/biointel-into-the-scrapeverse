import { render, screen } from '@testing-library/react'
import Home from '../app/page'

describe('BioIntel Guardian Home', () => {
  beforeEach(() => {
    // Reset state before each test
    ;(document.body.innerHTML = '')
  })

  test('renders header branding', () => {
    render(<Home />)
    expect(screen.getByText('BioIntel Guardian')).toBeInTheDocument()
  })

  test('renders tagline', () => {
    render(<Home />)
    expect(screen.getByText('Biomedical Data Integrity Monitor')).toBeInTheDocument()
  })

  test('renders hero section', () => {
    render(<Home />)
    expect(screen.getByText('AI-POWERED DATA INTEGRITY')).toBeInTheDocument()
    expect(screen.getByText('Biomedical Data Health Dashboard')).toBeInTheDocument()
  })

  test('renders monitored sources section heading', () => {
    render(<Home />)
    expect(screen.getByText('Monitored Sources')).toBeInTheDocument()
  })

  test('renders 3 source cards', () => {
    render(<Home />)
    const cards = screen.getAllByRole('button', {
      selector: 'button.w-full',
    })
    expect(cards).toHaveLength(3)
  })

  test('source cards display correct confidence percentages', () => {
    render(<Home />)
    expect(screen.getByText('98%')).toBeInTheDocument() // Clinical Data
    expect(screen.getByText('96%')).toBeInTheDocument() // Drug Database
    expect(screen.getByText('42%')).toBeInTheDocument() // Research Source
  })

  test('source cards display status indicators', () => {
    render(<Home />)
    expect(screen.getByText('Healthy')).toBeInTheDocument()
    expect(screen.getByText('Drift Detected')).toBeInTheDocument()
    // SVG icons rendered instead of emojis
    const svgs = screen.getAllByClassName('hand-drawer-icon')
    expect(svgs).toHaveLength(2)
  })

  test('renders drift alert for Research Source', () => {
    render(<Home />)
    // Click the Research Source card to select it
    const researchCard = screen.getByText('Research Source')
    expect(researchCard).toBeInTheDocument()

    // The alert should be present initially or after selection
    // Based on initial state, Research Source has status 'Drift Detected'
    expect(screen.getByText('SCRAPER DRIFT DETECTED')).toBeInTheDocument()
    expect(screen.getByText('42%')).toBeInTheDocument()
  })

  test('renders timeline events', () => {
    render(<Home />)
    const events = screen.getAllByText(/10:\d{2}/)
    expect(events).toHaveLength(5)
  })

  test('timeline events contain expected text', () => {
    render(<Home />)
    expect(screen.getByText('Scrape completed')).toBeInTheDocument()
    expect(screen.getByText('Payload validated')).toBeInTheDocument()
    expect(screen.getByText('Structural variation noticed')).toBeInTheDocument()
    expect(screen.getByText('AI drift detected')).toBeInTheDocument()
    expect(screen.getByText('Self-healing review triggered')).toBeInTheDocument()
  })

  test('renders overall system health', () => {
    render(<Home />)
    expect(screen.getByText('OVERALL SYSTEM HEALTH')).toBeInTheDocument()
    expect(screen.getByText('HEALTHY')).toBeInTheDocument()
    expect(screen.getByText('97%')).toBeInTheDocument()
  })

  test('renders integrity event timeline section heading', () => {
    render(<Home />)
    expect(screen.getByText('Integrity Event Timeline')).toBeInTheDocument()
  })

  test('footer pitch text is present', () => {
    render(<Home />)
    expect(screen.getByText('BioIntel Guardian is an AI-powered integrity layer')).toBeInTheDocument()
  })

  test('toggle selects research source and shows drift alert', async () => {
    render(<Home />)
    const researchCard = screen.getByText('Research Source')
    await researchCard.click()

    // Should show drift alert with 42% confidence
    expect(screen.getByText('AI DRIFT ALERT')).toBeInTheDocument()
    expect(screen.getByText('SCRAPER DRIFT DETECTED')).toBeInTheDocument()
    expect(screen.getByText('42%')).toBeInTheDocument()
  })
})