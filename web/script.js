const timelineEl = document.getElementById('timeline');
const cashEl = document.getElementById('cash');
const revenueEl = document.getElementById('revenue');
const expensesEl = document.getElementById('expenses');
const valuationEl = document.getElementById('valuation');
const moraleEl = document.getElementById('morale');
const innovationEl = document.getElementById('innovation');
const reputationEl = document.getElementById('reputation');
const debtEl = document.getElementById('debt');
const actionsRemainingEl = document.getElementById('actions-remaining');
const marketsContainer = document.getElementById('markets');
const logEl = document.getElementById('log');
const aiContainer = document.getElementById('ai-companies');
const productListEl = document.getElementById('product-list');
const actionDescriptionEl = document.getElementById('action-description');
const valuationCanvas = document.getElementById('valuation-chart');
const valuationCtx = valuationCanvas.getContext('2d');

const modalEl = document.getElementById('modal');
const modalTitleEl = document.getElementById('modal-title');
const modalBodyEl = document.getElementById('modal-body');
const modalConfirmEl = document.getElementById('modal-confirm');
const modalCancelEl = document.getElementById('modal-cancel');

const actionDetails = {
  launch: {
    title: 'Launch Neon Product',
    description:
      'Invest capital to ship a synthwave-inspired product into a market of your choice. Boosts share, reputation, and future revenue.',
  },
  marketing: {
    title: 'Run Marketing Blitz',
    description:
      'Flashy trade shows, vaporwave commercials, and magazine spreads energise the crowd. Raises reputation and morale while nudging market share.',
  },
  hire: {
    title: 'Hire Elite Talent',
    description:
      'Recruit legendary engineers from the arcade halls. Improves innovation, morale, and product performance.',
  },
  rnd: {
    title: 'R&D Hyper Sprint',
    description:
      'Focus the labs on radical experiments. Innovation skyrockets and markets get excited for the next big reveal.',
  },
  loan: {
    title: 'Secure Retro Loan',
    description:
      'Accept funding from a neon-clad venture banker. Gain cash now with quarterly interest payments.',
  },
  repay: {
    title: 'Service Debt',
    description:
      'Pay down principal to cut interest costs and keep creditors cool.',
  },
  advance: {
    title: 'Advance Quarter',
    description:
      'Lock in this quarter’s outcomes, process events, and face rival moves. Refreshes available actions.',
  },
};

const productNames = [
  'Neon Nexus OS',
  'HyperDrive Cloud',
  'SynthWave Console',
  'Circuit City CRM',
  'LaserLink Modem',
  'Chromatic AI Suite',
  'Quantum Pulse Chipset',
  'Midnight Matrix VR',
  'PixelPay Network',
  'RetroVision HUD',
  'Arcade Analytics',
  'Flux Capacitor Drive',
  'VaporChat Social',
  'TurboTape Backup',
  'Celestial Compute Grid',
  'IonBeam Robotics',
  'ByteRider Drone',
  'HoloSynth Entertainment',
  'Lumen Ledger',
  'Photon Courier Platform',
];

const marketsBlueprint = [
  { name: 'Artificial Intelligence', baseValue: 8000000, hype: 0.95, volatility: 0.35 },
  { name: 'Cloud Computing', baseValue: 6500000, hype: 0.82, volatility: 0.3 },
  { name: 'Cybersecurity', baseValue: 5600000, hype: 0.74, volatility: 0.28 },
  { name: 'Enterprise SaaS', baseValue: 5000000, hype: 0.68, volatility: 0.24 },
  { name: 'E-Commerce', baseValue: 5400000, hype: 0.71, volatility: 0.22 },
  { name: 'Consumer Hardware', baseValue: 4700000, hype: 0.62, volatility: 0.32 },
  { name: 'FinTech', baseValue: 5900000, hype: 0.77, volatility: 0.27 },
  { name: 'Social Media', baseValue: 5200000, hype: 0.7, volatility: 0.26 },
];

const aiDescriptors = [
  { name: 'SynthDyne Systems', style: 'Cutthroat', color: '#ff5db1' },
  { name: 'NovaGrid Labs', style: 'Visionary', color: '#00d7ff' },
  { name: 'ByteForge Dynamics', style: 'Efficient', color: '#ffd166' },
  { name: 'Omnitech Verse', style: 'Experimental', color: '#95ff8f' },
  { name: 'Hyperion Signal', style: 'Aggressive', color: '#ff8b5f' },
];

const eventDeck = [
  {
    name: 'Dot Matrix Buzz',
    description: 'RetroTech magazine features your founder on the cover.',
    effect(state) {
      state.reputation = clamp(state.reputation + 7, 0, 100);
      state.morale = clamp(state.morale + 4, 0, 100);
      addLog('RetroTech cover story boosts your brand aura.', 'positive');
    },
  },
  {
    name: 'Arcade Expo Triumph',
    description: 'Your booth steals the spotlight with neon vapor trails.',
    effect(state) {
      state.markets.forEach((market) => {
        market.playerShare = clamp(market.playerShare + 1.8 + Math.random() * 2, 0, 95);
        market.aiShare = Math.max(0, 100 - market.playerShare);
      });
      state.revenue += 120000;
      addLog('Arcade Expo crowds chant your name. Orders spike.', 'positive');
    },
  },
  {
    name: 'Hardware Shortage',
    description: 'A supply chain hiccup limits chip availability.',
    effect(state) {
      if (state.products.length === 0) {
        addLog('Hardware shortage looms, but you have no hardware products yet.', 'warning');
        return;
      }
      const penalty = Math.round(90000 + Math.random() * 60000);
      state.expenses += penalty;
      state.cash -= penalty;
      state.innovation = clamp(state.innovation - 4, 0, 120);
      addLog('Component shortage hikes costs and slows R&D.', 'negative');
    },
  },
  {
    name: 'Talent Exodus',
    description: 'Rival recruiters stalk your break room.',
    effect(state) {
      state.morale = clamp(state.morale - 6, 0, 100);
      state.reputation = clamp(state.reputation - 3, 0, 100);
      addLog('A rival poaches a beloved engineer. Team morale dips.', 'negative');
    },
  },
  {
    name: 'Collector Craze',
    description: 'Collectors bid on your limited edition hardware.',
    effect(state) {
      const bonus = Math.round(100000 + Math.random() * 90000);
      state.cash += bonus;
      state.revenue += Math.round(bonus * 0.4);
      addLog('Collectors flock to your neon hardware. Cash surges.', 'positive');
    },
  },
  {
    name: 'Retro Regulations',
    description: 'New compliance paperwork bogs everyone down.',
    effect(state) {
      const drag = Math.round(60000 + Math.random() * 40000);
      state.expenses += drag;
      state.cash -= drag;
      addLog('Regulators demand extra filings. Expenses climb.', 'warning');
    },
  },
  {
    name: 'Arc Reactor Breakthrough',
    description: 'Your labs pioneer a dazzling power efficiency trick.',
    effect(state) {
      state.innovation = clamp(state.innovation + 9, 0, 130);
      state.revenue += 90000;
      addLog('Breakthrough tech electrifies investors.', 'positive');
    },
  },
];

function createInitialState() {
  const markets = marketsBlueprint.map((market) => {
    const playerShare = randomRange(3, 9);
    return {
      ...market,
      playerShare,
      aiShare: Math.max(0, 100 - playerShare),
      previousShare: playerShare,
      lastDelta: 0,
      narrative: 'Awaiting disruption...',
      previousHype: market.hype,
    };
  });

  return {
    year: 1984,
    quarter: 1,
    cash: 750000,
    revenue: 0,
    expenses: 0,
    valuation: 2500000,
    morale: 68,
    innovation: 55,
    reputation: 48,
    debt: 0,
    actionsRemaining: 2,
    products: [],
    loans: [],
    markets,
    aiCompanies: generateAiCompanies(),
    availableProductNames: [...productNames],
    history: [2500000],
    turn: 0,
    gameOver: false,
    lastDebtService: 0,
  };
}

function generateAiCompanies() {
  return aiDescriptors.map((descriptor, index) => ({
    ...descriptor,
    valuation: Math.round(3500000 + index * 950000 + Math.random() * 500000),
    reputation: 55 + Math.random() * 20,
    morale: 60 + Math.random() * 20,
    narrative: 'Scheming in the neon shadows...'
  }));
}

let gameState = createInitialState();

function clamp(value, min, max) {
  return Math.min(Math.max(value, min), max);
}

function randomRange(min, max) {
  return Math.random() * (max - min) + min;
}

function formatMoney(value) {
  const sign = value < 0 ? '-' : '';
  const absValue = Math.abs(Math.round(value));
  return `${sign}$${absValue.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',')}`;
}

function describeHype(hype) {
  if (hype >= 1.05) return 'Explosive';
  if (hype >= 0.85) return 'High';
  if (hype >= 0.6) return 'Steady';
  return 'Cooling';
}

function describeVolatility(volatility) {
  if (volatility >= 0.35) return 'Wild';
  if (volatility >= 0.28) return 'Active';
  if (volatility >= 0.22) return 'Calm';
  return 'Stable';
}

function drawProductName() {
  if (gameState.availableProductNames.length === 0) {
    return `Technopoly MK-${Math.floor(Math.random() * 90 + 10)}`;
  }
  const index = Math.floor(Math.random() * gameState.availableProductNames.length);
  const [name] = gameState.availableProductNames.splice(index, 1);
  return name;
}

function hasActionsAvailable() {
  if (gameState.gameOver) {
    addLog('Simulation concluded. Restart to continue.', 'warning');
    return false;
  }
  if (gameState.actionsRemaining <= 0) {
    addLog('No command cycles remain this quarter. Advance the clock.', 'warning');
    return false;
  }
  return true;
}

function spendAction() {
  gameState.actionsRemaining = Math.max(0, gameState.actionsRemaining - 1);
  if (gameState.actionsRemaining === 0) {
    addLog('Command console cooling down. Advance the quarter to refresh actions.', 'system');
  }
  renderStatus();
}

function spendCash(amount) {
  gameState.cash -= amount;
}

function creditCash(amount) {
  gameState.cash += amount;
}

function openModal({ title, body, confirmText = 'Confirm', cancelText = 'Cancel', onConfirm, onCancel, hideCancel = false }) {
  modalTitleEl.textContent = title;
  modalBodyEl.innerHTML = '';
  if (typeof body === 'string') {
    modalBodyEl.innerHTML = `<p>${body}</p>`;
  } else {
    modalBodyEl.appendChild(body);
  }
  modalConfirmEl.textContent = confirmText;
  modalCancelEl.textContent = cancelText;
  modalCancelEl.classList.toggle('is-hidden', hideCancel);
  modalConfirmEl.classList.toggle('is-hidden', !onConfirm);

  modalConfirmEl.onclick = () => {
    if (!onConfirm) {
      closeModal();
      return;
    }
    const result = onConfirm();
    if (result !== false) {
      closeModal();
    }
  };

  modalCancelEl.onclick = () => {
    if (onCancel) {
      onCancel();
    }
    closeModal();
  };

  modalEl.classList.remove('hidden');
}

function closeModal() {
  modalEl.classList.add('hidden');
}

modalEl.addEventListener('click', (event) => {
  if (event.target === modalEl) {
    closeModal();
  }
});

function render() {
  renderStatus();
  updateTimeline();
  renderProducts();
  renderMarkets();
  renderAiCompanies();
  drawValuationChart();
}

function renderStatus() {
  cashEl.textContent = formatMoney(gameState.cash);
  revenueEl.textContent = formatMoney(gameState.revenue);
  expensesEl.textContent = formatMoney(gameState.expenses);
  valuationEl.textContent = formatMoney(gameState.valuation);
  moraleEl.textContent = `${Math.round(gameState.morale)}`;
  innovationEl.textContent = `${Math.round(gameState.innovation)}`;
  reputationEl.textContent = `${Math.round(gameState.reputation)}`;
  debtEl.textContent = formatMoney(gameState.debt);
  actionsRemainingEl.textContent = `${gameState.actionsRemaining}`;
}

function updateTimeline() {
  timelineEl.textContent = `Year ${gameState.year} · Quarter ${gameState.quarter}`;
}

function renderProducts() {
  productListEl.innerHTML = '';
  if (gameState.products.length === 0) {
    productListEl.classList.add('empty');
    productListEl.textContent = 'No products launched yet.';
    return;
  }
  productListEl.classList.remove('empty');
  gameState.products.forEach((product) => {
    const card = document.createElement('div');
    card.className = 'product-card';

    const name = document.createElement('div');
    name.className = 'name';
    name.textContent = product.name;

    const market = document.createElement('div');
    market.className = 'market';
    market.textContent = product.market;

    const quality = document.createElement('div');
    quality.className = 'stat';
    quality.innerHTML = `<span>Quality</span><span>${product.quality}</span>`;

    const revenue = document.createElement('div');
    revenue.className = 'stat';
    revenue.innerHTML = `<span>Base Rev.</span><span>${formatMoney(product.baseRevenue)}</span>`;

    card.append(name, market, quality, revenue);
    productListEl.appendChild(card);
  });
}

function renderMarkets() {
  marketsContainer.innerHTML = '';
  gameState.markets.forEach((market) => {
    const card = document.createElement('div');
    card.className = 'market-card';

    const title = document.createElement('div');
    title.className = 'market-title';
    title.textContent = market.name;

    const meta = document.createElement('div');
    meta.className = 'market-meta';
    meta.innerHTML = `<span>Hype: ${describeHype(market.hype)}</span><span>Volatility: ${describeVolatility(market.volatility)}</span>`;

    const shareBar = document.createElement('div');
    shareBar.className = 'share-bar';
    const playerBar = document.createElement('div');
    playerBar.className = 'player';
    playerBar.style.width = `${clamp(market.playerShare, 0, 100).toFixed(1)}%`;
    const aiBar = document.createElement('div');
    aiBar.className = 'ai';
    aiBar.style.width = `${clamp(market.aiShare, 0, 100).toFixed(1)}%`;
    shareBar.append(playerBar, aiBar);

    const trend = document.createElement('div');
    trend.className = 'trend';
    const arrow = market.lastDelta > 0.3 ? '▲' : market.lastDelta < -0.3 ? '▼' : '◆';
    trend.textContent = `Player share: ${market.playerShare.toFixed(1)}% ${arrow}`;

    const narrative = document.createElement('div');
    narrative.className = 'trend';
    narrative.textContent = market.narrative;

    card.append(title, meta, shareBar, trend, narrative);
    marketsContainer.appendChild(card);
  });
}

function renderAiCompanies() {
  aiContainer.innerHTML = '';
  gameState.aiCompanies.forEach((ai) => {
    const card = document.createElement('div');
    card.className = 'ai-card';

    const name = document.createElement('div');
    name.className = 'name';
    name.style.color = ai.color;
    name.textContent = ai.name;

    const style = document.createElement('div');
    style.className = 'stat';
    style.innerHTML = `<span>Persona</span><span>${ai.style}</span>`;

    const valuation = document.createElement('div');
    valuation.className = 'stat';
    valuation.innerHTML = `<span>Valuation</span><span>${formatMoney(ai.valuation)}</span>`;

    const reputation = document.createElement('div');
    reputation.className = 'stat';
    reputation.innerHTML = `<span>Reputation</span><span>${Math.round(ai.reputation)}</span>`;

    const morale = document.createElement('div');
    morale.className = 'stat';
    morale.innerHTML = `<span>Morale</span><span>${Math.round(ai.morale)}</span>`;

    const narrative = document.createElement('div');
    narrative.className = 'stat';
    narrative.style.justifyContent = 'flex-start';
    narrative.style.color = 'rgba(255, 255, 255, 0.7)';
    narrative.textContent = ai.narrative;

    card.append(name, style, valuation, reputation, morale, narrative);
    aiContainer.appendChild(card);
  });
}

function drawValuationChart() {
  const { width, height } = valuationCanvas;
  valuationCtx.clearRect(0, 0, width, height);

  valuationCtx.fillStyle = 'rgba(4, 8, 24, 0.9)';
  valuationCtx.fillRect(0, 0, width, height);

  const data = gameState.history.slice(-24);
  if (data.length < 2) {
    return;
  }

  const maxVal = Math.max(...data);
  const minVal = Math.min(...data);
  const range = maxVal - minVal || 1;

  valuationCtx.strokeStyle = '#00ffd0';
  valuationCtx.lineWidth = 2;
  valuationCtx.beginPath();
  data.forEach((val, index) => {
    const x = (index / (data.length - 1)) * (width - 30) + 15;
    const y = height - ((val - minVal) / range) * (height - 30) - 15;
    if (index === 0) {
      valuationCtx.moveTo(x, y);
    } else {
      valuationCtx.lineTo(x, y);
    }
  });
  valuationCtx.stroke();

  valuationCtx.fillStyle = 'rgba(0, 255, 208, 0.12)';
  valuationCtx.lineTo(width - 15, height - 15);
  valuationCtx.lineTo(15, height - 15);
  valuationCtx.closePath();
  valuationCtx.fill();
}

function addLog(message, tone = 'system') {
  const entry = document.createElement('div');
  entry.className = `log-entry ${tone}`;
  entry.textContent = message;
  logEl.appendChild(entry);
  while (logEl.children.length > 80) {
    logEl.removeChild(logEl.firstChild);
  }
}

function updateValuation() {
  const productValue = gameState.products.reduce((total, product) => total + product.baseRevenue * 6, 0);
  const intangible = (gameState.reputation + gameState.innovation) * 9500;
  const baseline = gameState.cash * 1.1 + gameState.revenue * 4;
  const marketBonus = gameState.markets.reduce((total, market) => total + market.playerShare * (market.baseValue / 16), 0);
  gameState.valuation = Math.max(1000000, Math.round(baseline + productValue + intangible + marketBonus));
}

function updateMarketNarratives() {
  gameState.markets.forEach((market) => {
    const hypeDescriptor = describeHype(market.hype);
    let shareDescriptor = 'Presence minimal.';
    if (market.playerShare > 35) {
      shareDescriptor = 'Your neon signage dominates expo floors.';
    } else if (market.playerShare > 20) {
      shareDescriptor = 'Growing cult following among enthusiasts.';
    } else if (market.playerShare > 8) {
      shareDescriptor = 'Rumblings of interest echo through forums.';
    }
    const movement = market.lastDelta > 0.3 ? 'Momentum rising.' : market.lastDelta < -0.3 ? 'Competitors press harder.' : 'Holding the line.';
    market.narrative = `${hypeDescriptor} hype. ${movement} ${shareDescriptor}`;
  });
}

function advanceQuarter() {
  if (gameState.gameOver) {
    addLog('Simulation concluded. Restart to play again.', 'warning');
    return;
  }

  const unusedActions = gameState.actionsRemaining;
  if (unusedActions > 0) {
    addLog(`Advancing with ${unusedActions} unused action(s).`, 'system');
  }

  gameState.actionsRemaining = 2;
  gameState.quarter += 1;
  if (gameState.quarter > 4) {
    gameState.quarter = 1;
    gameState.year += 1;
  }
  gameState.turn += 1;

  let totalRevenue = 0;
  let totalExpenses = 0;

  gameState.markets.forEach((market) => {
    const previousShare = market.playerShare;
    const activeProducts = gameState.products.filter((product) => product.market === market.name);
    if (activeProducts.length > 0) {
      const hypeMultiplier = 0.8 + market.hype * 0.6;
      const innovationBonus = 0.6 + gameState.innovation / 160;
      const randomness = 0.82 + Math.random() * 0.32;
      const shareFactor = market.playerShare / 100;
      const marketRevenue = (market.baseValue / 4) * shareFactor * hypeMultiplier * innovationBonus * randomness;
      totalRevenue += marketRevenue;
      const upkeep = activeProducts.length * 52000 + shareFactor * 38000;
      totalExpenses += upkeep;
    }

    const erosionBase = randomRange(0.6, 2.4) * market.volatility * 2.6;
    const reputationShield = gameState.reputation / 70;
    const erosion = Math.max(0, erosionBase - reputationShield);
    market.playerShare = clamp(market.playerShare - erosion + gameState.innovation / 240, 0, 96);
    market.aiShare = Math.max(0, 100 - market.playerShare);
    market.lastDelta = market.playerShare - previousShare;

    const hypeDrift = (Math.random() - 0.45) * market.volatility * 0.22;
    market.previousHype = market.hype;
    market.hype = clamp(market.hype + hypeDrift, 0.35, 1.35);
  });

  gameState.products.forEach((product) => {
    const maturityBonus = 1 + Math.min(gameState.turn - product.launchedTurn, 6) * 0.03;
    product.baseRevenue = Math.round(product.baseRevenue * (0.98 + Math.random() * 0.08) * maturityBonus);
  });

  const payroll = 140000 + gameState.products.length * 22000 + gameState.morale * 600;
  const research = Math.max(0, (gameState.innovation - 40) * 2600);
  totalExpenses += payroll + research;

  let debtService = 0;
  gameState.loans.forEach((loan) => {
    const interestPayment = Math.round((loan.amount * loan.rate) / 4);
    debtService += interestPayment;
  });
  totalExpenses += debtService;
  gameState.lastDebtService = debtService;

  gameState.revenue = Math.round(totalRevenue);
  gameState.expenses = Math.round(totalExpenses);
  gameState.cash += Math.round(totalRevenue - totalExpenses);

  if (gameState.debt > 0) {
    gameState.debt = Math.round(gameState.loans.reduce((sum, loan) => sum + loan.amount, 0));
  }

  gameState.morale = clamp(gameState.morale + randomRange(-4, 3) + gameState.revenue / 600000 - debtService / 90000, 0, 100);
  gameState.innovation = clamp(gameState.innovation + randomRange(-2, 3) + gameState.products.length * 0.3, 0, 130);
  gameState.reputation = clamp(gameState.reputation + randomRange(-1, 2), 0, 100);

  processRandomEvent();
  rivalTurns();
  updateValuation();
  updateMarketNarratives();

  gameState.debt = Math.round(gameState.loans.reduce((sum, loan) => sum + loan.amount, 0));

  gameState.history.push(gameState.valuation);
  if (gameState.history.length > 96) {
    gameState.history.shift();
  }

  addLog(`Quarter ${gameState.quarter} of ${gameState.year} processed. Revenue ${formatMoney(gameState.revenue)} · Expenses ${formatMoney(gameState.expenses)}.`, 'system');

  render();
  evaluateEndConditions();
}

function processRandomEvent() {
  if (Math.random() < 0.6) {
    const event = eventDeck[Math.floor(Math.random() * eventDeck.length)];
    addLog(`[Event] ${event.name}: ${event.description}`, 'system');
    event.effect(gameState);
  }
}

function rivalTurns() {
  gameState.aiCompanies.forEach((ai) => {
    const roll = Math.random();
    const targetMarket = gameState.markets[Math.floor(Math.random() * gameState.markets.length)];
    if (roll < 0.33) {
      const squeeze = randomRange(1.5, 3.8);
      targetMarket.playerShare = clamp(targetMarket.playerShare - squeeze, 0, 95);
      targetMarket.aiShare = Math.max(0, 100 - targetMarket.playerShare);
      ai.valuation = Math.round(ai.valuation * (1.02 + Math.random() * 0.03));
      ai.narrative = `Flooded ${targetMarket.name} with promos.`;
      addLog(`${ai.name} floods ${targetMarket.name} with promotions.`, 'negative');
    } else if (roll < 0.66) {
      const steal = randomRange(1.2, 2.4);
      gameState.reputation = clamp(gameState.reputation - 2, 0, 100);
      targetMarket.playerShare = clamp(targetMarket.playerShare - steal, 0, 95);
      targetMarket.aiShare = Math.max(0, 100 - targetMarket.playerShare);
      ai.reputation = clamp(ai.reputation + 3, 0, 100);
      ai.narrative = 'Captured headlines with a flashy reveal.';
      addLog(`${ai.name} steals your spotlight with a retro-futuristic reveal.`, 'warning');
    } else {
      const moraleHit = randomRange(3, 6);
      gameState.morale = clamp(gameState.morale - moraleHit, 0, 100);
      ai.morale = clamp(ai.morale + 2, 0, 100);
      ai.narrative = 'Poached a key technomancer from your labs.';
      addLog(`${ai.name} poaches a key technomancer. Morale suffers.`, 'negative');
    }

    const drift = 1 + (Math.random() - 0.45) * 0.08;
    ai.valuation = Math.max(1500000, Math.round(ai.valuation * drift));
  });
}

function evaluateEndConditions() {
  if (gameState.gameOver) {
    return;
  }
  if (gameState.cash <= -350000 || gameState.morale <= 5 || gameState.debt >= 1500000) {
    triggerGameOver(
      'loss',
      'Cash reserves depleted and morale collapsed. The neon lights flicker out at Technopoly HQ.'
    );
    return;
  }
  if (gameState.valuation >= 75000000 || gameState.reputation >= 92) {
    triggerGameOver(
      'win',
      'Your retro-futuristic empire now dominates the silicon skyline. Investors chant your name.'
    );
  }
}

function triggerGameOver(type, message) {
  gameState.gameOver = true;
  addLog(message, type === 'win' ? 'positive' : 'negative');
  openModal({
    title: type === 'win' ? 'Victory Protocol' : 'Shutdown Warning',
    body: message,
    confirmText: 'Restart Simulation',
    cancelText: 'Close',
    onConfirm: () => {
      restartGame();
      return true;
    },
    onCancel: null,
    hideCancel: true,
  });
}

function restartGame() {
  gameState = createInitialState();
  logEl.innerHTML = '';
  addLog('Simulation rebooted. Technopoly returns to the neon frontier.', 'system');
  render();
}

function handleLaunchProduct() {
  if (!hasActionsAvailable()) {
    return;
  }

  const container = document.createElement('div');
  container.innerHTML = '<p>Select a market to deploy your latest neon invention.</p>';

  const select = document.createElement('select');
  gameState.markets.forEach((market) => {
    const option = document.createElement('option');
    option.value = market.name;
    option.textContent = `${market.name} · Hype ${describeHype(market.hype)}`;
    select.appendChild(option);
  });
  container.appendChild(select);

  openModal({
    title: 'Launch Neon Product',
    body: container,
    confirmText: 'Deploy',
    onConfirm: () => {
      const marketName = select.value;
      const market = gameState.markets.find((m) => m.name === marketName);
      const launchCost = 200000;
      if (gameState.cash < launchCost) {
        addLog(`Need ${formatMoney(launchCost)} to launch.`, 'warning');
        return false;
      }
      spendCash(launchCost);
      const quality = Math.round(60 + Math.random() * 30 + gameState.innovation * 0.25);
      const baseRevenue = Math.round(market.baseValue * randomRange(0.05, 0.11));
      const product = {
        id: `${Date.now()}-${Math.floor(Math.random() * 999)}`,
        name: drawProductName(),
        market: market.name,
        quality,
        baseRevenue,
        launchedTurn: gameState.turn,
      };
      gameState.products.push(product);
      market.playerShare = clamp(market.playerShare + 6 + quality / 18 + gameState.reputation / 25, 0, 96);
      market.aiShare = Math.max(0, 100 - market.playerShare);
      gameState.innovation = clamp(gameState.innovation + 5 + Math.random() * 3, 0, 130);
      gameState.reputation = clamp(gameState.reputation + 4 + Math.random() * 2, 0, 100);
      addLog(`Product launch success! ${product.name} hits ${market.name}.`, 'positive');
      spendAction();
      render();
      return true;
    },
  });
}

function runMarketingBlitz() {
  const cost = 100000;
  if (!hasActionsAvailable() || gameState.cash < cost) {
    if (gameState.cash < cost) {
      addLog(`Marketing blitz requires ${formatMoney(cost)}.`, 'warning');
    }
    return;
  }
  spendCash(cost);
  const repGain = Math.round(randomRange(6, 11));
  const moraleGain = Math.round(randomRange(3, 6));
  gameState.reputation = clamp(gameState.reputation + repGain, 0, 100);
  gameState.morale = clamp(gameState.morale + moraleGain, 0, 100);
  gameState.markets.forEach((market) => {
    const boost = randomRange(0.6, 1.6);
    market.playerShare = clamp(market.playerShare + boost, 0, 95);
    market.aiShare = Math.max(0, 100 - market.playerShare);
  });
  addLog(`Marketing blitz dazzles the airwaves. Reputation +${repGain}, morale +${moraleGain}.`, 'positive');
  spendAction();
  render();
}

function hireTalent() {
  const cost = 75000;
  if (!hasActionsAvailable() || gameState.cash < cost) {
    if (gameState.cash < cost) {
      addLog(`Elite talent demands ${formatMoney(cost)} signing bonuses.`, 'warning');
    }
    return;
  }
  spendCash(cost);
  const innovationBoost = randomRange(5, 9);
  const moraleBoost = randomRange(5, 8);
  gameState.innovation = clamp(gameState.innovation + innovationBoost, 0, 130);
  gameState.morale = clamp(gameState.morale + moraleBoost, 0, 100);
  gameState.products.forEach((product) => {
    product.baseRevenue = Math.round(product.baseRevenue * (1 + innovationBoost / 140));
  });
  addLog('Legendary engineers join Technopoly. Innovation soars.', 'positive');
  spendAction();
  render();
}

function researchSprint() {
  const cost = 60000;
  if (!hasActionsAvailable() || gameState.cash < cost) {
    if (gameState.cash < cost) {
      addLog(`R&D sprint needs ${formatMoney(cost)} in lab equipment.`, 'warning');
    }
    return;
  }
  spendCash(cost);
  const innovationGain = randomRange(7, 12);
  const hypeBoost = randomRange(0.03, 0.08);
  gameState.innovation = clamp(gameState.innovation + innovationGain, 0, 135);
  gameState.markets.forEach((market) => {
    market.hype = clamp(market.hype + hypeBoost - market.volatility * 0.02, 0.35, 1.4);
  });
  addLog('R&D labs glow electric blue. Innovation leaps forward.', 'positive');
  spendAction();
  render();
}

function secureLoan() {
  if (!hasActionsAvailable()) {
    return;
  }
  const container = document.createElement('div');
  container.innerHTML = '<p>Select funding to wire from the retro bank (50k - 500k).</p>';
  const input = document.createElement('input');
  input.type = 'number';
  input.min = '50000';
  input.max = '500000';
  input.step = '5000';
  input.value = '150000';
  container.appendChild(input);

  openModal({
    title: 'Secure Retro Loan',
    body: container,
    confirmText: 'Accept Funds',
    onConfirm: () => {
      const amount = Number(input.value);
      if (Number.isNaN(amount) || amount < 50000) {
        addLog('Minimum loan is $50,000.', 'warning');
        return false;
      }
      if (amount > 500000) {
        addLog('Retro banker declines anything above $500,000.', 'warning');
        return false;
      }
      creditCash(amount);
      gameState.loans.push({ amount, rate: 0.08 });
      gameState.debt = Math.round(gameState.loans.reduce((sum, loan) => sum + loan.amount, 0));
      addLog(`Loan secured for ${formatMoney(amount)} at 8% APR.`, 'system');
      spendAction();
      render();
      return true;
    },
  });
}

function serviceDebt() {
  if (gameState.debt <= 0) {
    addLog('No outstanding debt to service.', 'system');
    return;
  }
  if (!hasActionsAvailable()) {
    return;
  }
  const container = document.createElement('div');
  container.innerHTML = `<p>Outstanding debt: ${formatMoney(gameState.debt)}. Enter payment amount.</p>`;
  const input = document.createElement('input');
  input.type = 'number';
  input.min = '25000';
  input.step = '5000';
  input.value = '50000';
  container.appendChild(input);

  openModal({
    title: 'Service Debt',
    body: container,
    confirmText: 'Submit Payment',
    onConfirm: () => {
      let amount = Number(input.value);
      if (Number.isNaN(amount) || amount <= 0) {
        addLog('Enter a valid payment amount.', 'warning');
        return false;
      }
      amount = Math.min(amount, gameState.debt);
      if (gameState.cash < amount) {
        addLog('Not enough cash to cover that payment.', 'warning');
        return false;
      }
      spendCash(amount);
      let remaining = amount;
      for (const loan of gameState.loans) {
        if (remaining <= 0) break;
        const pay = Math.min(loan.amount, remaining);
        loan.amount -= pay;
        remaining -= pay;
      }
      gameState.loans = gameState.loans.filter((loan) => loan.amount > 0);
      gameState.debt = Math.round(gameState.loans.reduce((sum, loan) => sum + loan.amount, 0));
      addLog(`Paid ${formatMoney(amount)} toward outstanding loans.`, 'positive');
      spendAction();
      render();
      return true;
    },
  });
}

const actions = {
  launch: handleLaunchProduct,
  marketing: runMarketingBlitz,
  hire: hireTalent,
  rnd: researchSprint,
  loan: secureLoan,
  repay: serviceDebt,
  advance: advanceQuarter,
};

document.querySelectorAll('[data-action]').forEach((button) => {
  const action = button.dataset.action;
  button.addEventListener('click', () => {
    const handler = actions[action];
    if (handler) {
      handler();
    }
  });
  button.addEventListener('mouseenter', () => {
    const info = actionDetails[action];
    if (info) {
      actionDescriptionEl.textContent = info.description;
    }
  });
  button.addEventListener('focus', () => {
    const info = actionDetails[action];
    if (info) {
      actionDescriptionEl.textContent = info.description;
    }
  });
});

document.querySelector('.actions-panel').addEventListener('mouseleave', () => {
  actionDescriptionEl.textContent =
    'Choose an action to guide Technopoly through the neon-lit markets of the future.';
});

addLog('Welcome to Technopoly: Retro Web Edition. Keep the neon lights glowing and outmaneuver rivals.', 'system');
render();
