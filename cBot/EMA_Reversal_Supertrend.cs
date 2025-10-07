using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class EMA_Reversal_Supertrend : Robot
    {
        [Parameter("100 EMA Period", DefaultValue = 100)]
        public int FastEMAPeriod { get; set; }

        [Parameter("300 EMA Period", DefaultValue = 300)]
        public int SlowEMAPeriod { get; set; }

        [Parameter("Supertrend Multiplier", DefaultValue = 30)]
        public double STMultiplier { get; set; }

        [Parameter("Supertrend Period", DefaultValue = 2)]
        public int STPeriod { get; set; }

        [Parameter("Stop Loss (pips)", DefaultValue = 5)]
        public double StopLoss { get; set; }

        private ExponentialMovingAverage fastEMA;
        private ExponentialMovingAverage slowEMA;
        private SuperTrend supertrend;

        protected override void OnStart()
        {
            fastEMA = Indicators.ExponentialMovingAverage(MarketSeries.Close, FastEMAPeriod);
            slowEMA = Indicators.ExponentialMovingAverage(MarketSeries.Close, SlowEMAPeriod);
            supertrend = Indicators.GetIndicator<SuperTrend>(STPeriod, STMultiplier);
        }

        protected override void OnBar()
        {
            var lastBar = MarketSeries.Close.Count - 2; // Last closed bar
            var currentBar = MarketSeries.Close.Count - 1;

            // Long Condition
            if (supertrend.Result[lastBar] > MarketSeries.Close[lastBar] && 
                fastEMA.Result[lastBar] > slowEMA.Result[lastBar] &&
                MarketSeries.Low[lastBar] < slowEMA.Result[lastBar] &&
                MarketSeries.Close[currentBar] > MarketSeries.Open[currentBar])
            {
                ExecuteMarketOrder(TradeType.Buy, SymbolName, 10000, "EMA_Reversal", StopLossInPips: StopLoss);
            }

            // Short Condition
            if (supertrend.Result[lastBar] < MarketSeries.Close[lastBar] &&
                fastEMA.Result[lastBar] < slowEMA.Result[lastBar] &&
                MarketSeries.High[lastBar] > slowEMA.Result[lastBar] &&
                MarketSeries.Close[currentBar] < MarketSeries.Open[currentBar])
            {
                ExecuteMarketOrder(TradeType.Sell, SymbolName, 10000, "EMA_Reversal", StopLossInPips: StopLoss);
            }

            // Close trades on Supertrend flip
            foreach (var position in Positions.FindAll("EMA_Reversal", SymbolName))
            {
                if (position.TradeType == TradeType.Buy && supertrend.Result[lastBar] < MarketSeries.Close[lastBar])
                    ClosePosition(position);

                if (position.TradeType == TradeType.Sell && supertrend.Result[lastBar] > MarketSeries.Close[lastBar])
                    ClosePosition(position);
            }
        }
    }
}
