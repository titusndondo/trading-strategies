import backtrader as bt


class quantiles(bt.Indicator):

    lines = ('linear_regression', )
    params = (
        ('window', 300),
        ('lookback', 60),
    )
    
    iter = 0
    
    def next(self):
        if (self.iter > self.params.window + 1 + self.params.lookback):
            
            raw_prices = self.data.get(size = self.params.window + 1 + self.params.lookback) #
            prices = np.array(raw_prices)
            
            returns = pd.Series(prices).pct_change(periods = 1)
            
            train_data = pd.DataFrame()
            for i in range(0, self.params.lookback + 1):
                series = returns.shift(periods = i)
                series.name = f"lag_{i}"
                train_data = pd.concat([train_data, series], axis = 1)
                
            train_data = train_data.dropna().iloc[:self.params.window]

            X = train_data.iloc[:, 1:]
            y = train_data.loc[:, 'lag_0']
            y = pd.Series(np.where(y > 0, 1, 0))
            
            clf = RandomForestClassifier()
            clf.fit(X, y)
            
            inputt = np.array(train_data.iloc[self.params.window - 1, ][:-1]).reshape(1, -1)
            prediction = clf.predict(inputt)
            self.lines.linear_regression[0] = prediction
            
            print(f"Iteration: {self.iter}. Prediction: {self.lines.linear_regression[0]}")
        self.iter += 1


class macdCrossOver(bt.Strategy):
    """

    A simple moving average convergence divergence (NACD) crossover strategy; 
    crossing of a fast and slow moving average generates buy/sell
    signals.

    """
    params = (
        ('fast', 12),
        ('slow', 26)
    )
 
    # logging function
    def log(self, txt, dt = None):
        """
        inputs: text to log - txt
                datetime - df

        output: time of event in iso-format
                text indicating the event
        """

        dt = dt or self.data.datetime.date(0)
        print(f"{dt.isoformat()}, {txt}")


    def __init__(self):
        """
        Initialize the strategy
        """

        # throw error if fastema greater than slowema
        if self.params.fast > self.params.slow:
            raise ValueError(
                "A MACD strategy cannot have the fast moving average's window be " + \
                "greater than the slow moving average window.")

        # house keeping objects
        self.order = None
        self.buyprice = None
        self.buycomm = None   
 
        # strategy objects
        self.macd = None
 
        # get close price
        self.dataclose = self.data.close

        # get MACD as diff between fast(12 day) and slow EMA(26 day)
        # and the signal as 9 day EMA of macd
        self.macd = btind.MACD(self.dataclose, period_me1 = 12, period_me2 = 26, period_signal = 9)
        

        # Cross of macd.macd and macd.signal
        self.mcross = bt.indicators.CrossOver(self.macd.macd, self.macd.signal)
 
    # event notification and order tracking
    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # do nothing
            pass
    
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(f"BUY EXECUTED: {order.executed.price}, {order.executed.value}, {order.executed.comm}")
            elif order.issell():
                self.log(f"SELL EXECUTED: {order.executed.price}, {order.executed.value}, {order.executed.comm}")
            self.bar_executed = len(self)
        elif order.status in [order.Cancelled, order.Margin, order.Rejected]:
            self.log(f"Order Cancelled, Margin, Rejected")
            
        # Write down: no pending order
        self.order = None

    # execute on bar by bar basis
    def next(self):

        """
        Define what will be done in a single step, including creating and closing trades
        """

        # Simply log the closing price of the series from the reference
        self.log(f"Close, {self.dataclose[0]}")
    
        # if processing an order, do nothing, avoid duplicating orders
        if self.order:
            return

        # if not in position
        if not self.position:  # Are we out of the market?
            # Consider the possibility of entrance
            # Notice the indexing; [0] always mens the present bar, and [-1] the bar immediately preceding
            # Thus, the condition below translates to: "If today the MACD is bullish (greater than
            # signal_line), go long"
            # if our conditions are met
            if self.mcross[0] < 0:
                # buy
                self.log(f"BUY CREATE: {self.dataclose[0]}")

                # keep track of the order to avoid making another one
                self.order = self.buy()
        
        # if in position, we might consider selling
        else:
            if self.mcross[0] > 0:
                # sell
                self.log(f"SELL CREATE: {self.dataclose[0]}")

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()