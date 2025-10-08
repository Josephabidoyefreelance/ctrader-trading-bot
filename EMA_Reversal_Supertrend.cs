using System;
using cAlgo.API;
using cAlgo.API.Indicators;
using cAlgo.API.Internals;

namespace cAlgo.Robots
{
    [Robot(TimeZone = TimeZones.UTC, AccessRights = AccessRights.None)]
    public class EMA_Reversal_Supertrend : Robot
    {
        // Parameters
        [Parameter("Supertrend Multiplier", DefaultValue = 30)]
        public double Multiplier { get; set; }

        [Parameter("Supertrend Periods", DefaultValue = 2)]
        public int Periods { get; set; }

        [Parameter("Stop Loss (Pips)", DefaultValue = 5)]
        public int StopLoss { get; set; }

        // Indicators
        private Supertrend supertrend;
        private ExponentialMovingAverage ema100;
        private ExponentialMovingAverage ema300;

        protected override void OnStart()
        {
            // Initialize indicators
            supertrend = Indicators.Supertrend(Periods, Multiplier);
            ema100 = Indicators.ExponentialMovingAverage(MarketSeries.Close, 100);
            ema300 = Indicators.ExponentialMovingAverage(MarketSeries.Close, 300);
        }

        protected override void OnBar()
        {
            // Get last bar values
            double lastBarLow = MarketSeries.Low.Last(1);
            double lastBarHigh = MarketSeries.High.Last(1);
            double currentClose = MarketSeries.Close.Last(0);
            double currentOpen = MarketSeries.Open.Last(0);

            // Buy condition
            if (supertrend.UpTrend.Last(1) > 0 && // Supertrend green
                ema100.Result.Last(1) > ema300.Result.Last(1) && // 100 EMA above 300 EMA
                lastBarLow < ema300.Result.Last(1) && // Last Renko bar low below 300 EMA
                currentClose > currentOpen) // Current bar green
            {
                ExecuteMarketOrder(TradeType.Buy, SymbolName, Symbol.NormalizeVolume(10000), "EMA_Reversal_Supertrend", StopLoss, 0);
            }

            // Sell condition
            if (supertrend.DownTrend.Last(1) > 0 && // Supertrend red
                ema100.Result.Last(1) < ema300.Result.Last(1) && // 100 EMA below 300 EMA
                lastBarHigh > ema300.Result.Last(1) && // Last Renko bar high above 300 EMA
                currentClose < currentOpen) // Current bar red
            {
                ExecuteMarketOrder(TradeType.Sell, SymbolName, Symbol.NormalizeVolume(10000), "EMA_Reversal_Supertrend", StopLoss, 0);
            }

            // Take Profit logic based on Supertrend reversal
            foreach (var position in Positions.FindAll("EMA_Reversal_Supertrend", SymbolName))
            {
                if (position.TradeType == TradeType.Buy && supertrend.DownTrend.Last(1) > 0)
                {
                    ClosePosition(position);
                }

                if (position.TradeType == TradeType.Sell && supertrend.UpTrend.Last(1) > 0)
                {
                    ClosePosition(position);
                }
            }
        }

        protected override void OnStop()
        {
            // Clean-up if needed
        }
    }
}
