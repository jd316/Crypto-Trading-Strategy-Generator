import streamlit as st
import sys
import os
import importlib
import traceback

# Function to check if required modules are available
def check_dependencies():
    """Check if all required dependencies are installed."""
    required_modules = {
        "streamlit": "streamlit",
        "pandas": "pandas",
        "numpy": "numpy", 
        "requests": "requests",
        "python-dotenv": "dotenv",
        "pandas_ta": "pandas_ta",
        "rpds-py": "rpds",
        "cryptography": "cryptography",
        "aiohttp": "aiohttp",
        "openai": "openai"
    }
    
    missing = []
    for package, module in required_modules.items():
        try:
            importlib.import_module(module)
        except ImportError:
            missing.append(package)
    
    return missing

# Check dependencies first
missing_deps = check_dependencies()
if missing_deps:
    st.error(f"Missing required dependencies: {', '.join(missing_deps)}")
    st.info("Please install missing packages with:")
    install_cmd = f"pip install {' '.join(missing_deps)}"
    st.code(install_cmd, language="bash")
    st.stop()

# Add the virtual environment to the path if needed
try:
    import pandas as pd
except ImportError:
    venv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv")
    if os.path.exists(venv_path):
        site_packages = os.path.join(venv_path, "Lib", "site-packages")
        if os.path.exists(site_packages) and site_packages not in sys.path:
            sys.path.insert(0, site_packages)
            print(f"Added {site_packages} to sys.path")

# Now try imports that might have initially failed
try:
    import pandas as pd
    from app.nlp_handler import interpret_user_input
    from app.strategy_generator import StrategyGenerator
    from app.backtester import run_backtest
    from app.data_handler import fetch_ohlc_data
except ImportError as e:
    st.error(f"Error importing required modules: {e}")
    st.info("Please install missing packages with: pip install -r requirements.txt")
    missing_package = str(e).split("'")[1] if "'" in str(e) else str(e)
    st.code(f"pip install {missing_package}", language="bash")
    st.stop()

# Version display
VERSION = "1.0.0"
st.set_page_config(
    page_title="Crypto Trading Strategy Generator",
    page_icon="📈",
    layout="wide"
)

# Streamlit UI
col1, col2 = st.columns([5, 1])
with col1:
    st.title("Crypto Trading Strategy Generator")
    st.write("This application uses Azure OpenAI integration for strategy generation.")
with col2:
    st.write(f"v{VERSION}")

# Initialize session state variables
if 'strategy_params' not in st.session_state:
    st.session_state.strategy_params = None

if 'ohlc_data' not in st.session_state:
    st.session_state.ohlc_data = None

if 'strategy_code' not in st.session_state:
    st.session_state.strategy_code = None

if 'backtest_results' not in st.session_state:
    st.session_state.backtest_results = None

# Session state flags
if 'data_visualized' not in st.session_state:
    st.session_state.data_visualized = False

if 'code_generated' not in st.session_state:
    st.session_state.code_generated = False

# Help Section
with st.expander("How to Enter Your Strategy"):
    st.write("""
    - **Entry Conditions**: Describe when to enter a trade (e.g., 'Buy when RSI < 30 and price crosses above SMA').
    - **Exit Conditions**: Describe when to exit a trade (e.g., 'Sell when RSI > 70').
    - **Asset**: Specify the cryptocurrency pair (e.g., 'BTC/USDT').
    - **Timeframe**: Specify the timeframe (e.g., '1h' for 1-hour candles).
    
    This application uses **Azure OpenAI** to interpret your natural language description and generate executable Python code.
    """)

    # Add example strategies
    st.subheader("Example Strategies")
    example1 = "Buy BTC when RSI(14) falls below 30 on a 4h timeframe, sell when RSI goes above 70"
    example2 = "Buy ETH when the 20-day EMA crosses above the 50-day EMA with volume increasing, sell when price drops 5% from peak"
    example3 = "Buy 0.5 BTC when the 20-period EMA crosses above the 50-period EMA and RSI(14) is below 40, exit when RSI(14) exceeds 70"
    
    if st.button("Example 1"):
        st.session_state.example_strategy = example1
    if st.button("Example 2"):
        st.session_state.example_strategy = example2
    if st.button("Example 3"):
        st.session_state.example_strategy = example3

# User input
if 'example_strategy' in st.session_state:
    user_input = st.text_area("Enter your trading strategy in natural language:", value=st.session_state.example_strategy)
    # Clear the example after it's been used
    st.session_state.pop('example_strategy', None)
else:
    user_input = st.text_area("Enter your trading strategy in natural language:")

# Step 1: Interpret user input
if st.button("Generate Strategy"):
    if user_input:
        with st.spinner("Interpreting strategy with Azure OpenAI..."):
            try:
                st.session_state.strategy_params = interpret_user_input(user_input)
                st.session_state.data_visualized = False
                st.session_state.code_generated = False
            except Exception as e:
                st.error(f"Error interpreting strategy: {str(e)}")
                st.error(f"Details: {traceback.format_exc()}")
    else:
        st.error("Please enter a valid strategy.")

# Display extracted strategy parameters
if st.session_state.strategy_params:
    st.write("Extracted Strategy Parameters:", st.session_state.strategy_params)

# Step 2: Fetch historical data
if st.session_state.strategy_params and not st.session_state.data_visualized:
    if st.button("Visualize Historical Data"):
        symbol = st.session_state.strategy_params.get('Asset', 'BTC/USDT').replace('/', '')
        timeframe = st.session_state.strategy_params.get('Timeframe', '1h')
        st.write(f"Fetching historical data for {symbol}...")
        with st.spinner("Fetching data from Binance..."):
            try:
                st.session_state.ohlc_data = fetch_ohlc_data(symbol, timeframe)
                if st.session_state.ohlc_data is not None and not st.session_state.ohlc_data.empty:
                    st.write("Fetched Data:", st.session_state.ohlc_data.head())
                    st.session_state.data_visualized = True
                    
                    # Show a quick chart of the closing prices
                    st.subheader(f"{symbol} Price Chart ({timeframe})")
                    st.line_chart(st.session_state.ohlc_data.set_index('timestamp')['close'])
                else:
                    st.error(f"Failed to fetch data. No data returned from Binance for {symbol} with timeframe {timeframe}.")
            except ValueError as e:
                st.error(f"Data Error: {str(e)}")
            except RuntimeError as e:
                st.error(f"Binance API Error: {str(e)}")
            except Exception as e:
                st.error(f"Unexpected error fetching data: {str(e)}")
                st.error(f"Details: {traceback.format_exc()}")

# Step 3: Generate strategy code
if st.session_state.data_visualized and not st.session_state.code_generated:
    if st.button("Get Code"):
        with st.spinner("Generating strategy code with Azure OpenAI..."):
            try:
                # Pass both strategy parameters and OHLCV data to the generator
                strategy_generator = StrategyGenerator(st.session_state.strategy_params)
                st.session_state.strategy_code = strategy_generator.generate_strategy()
                st.session_state.code_generated = True
            except Exception as e:
                st.error(f"Error generating strategy code: {str(e)}")
                st.error(f"Details: {traceback.format_exc()}")

# Display the generated code (always show if it exists)
if st.session_state.strategy_code:
    st.subheader("Generated Strategy Code")
    st.code(st.session_state.strategy_code, language="python")

# Step 4: Backtest the strategy
if st.session_state.code_generated and st.session_state.ohlc_data is not None:
    if st.button("Backtest This"):
        try:
            # Validate the generated code
            if not st.session_state.strategy_code or "def trading_strategy(" not in str(st.session_state.strategy_code):
                st.error("Generated code is invalid. Missing 'trading_strategy' function.")
            else:
                with st.spinner("Running backtest..."):
                    # Run backtest and store results
                    st.session_state.backtest_results = run_backtest(
                        st.session_state.strategy_code,
                        st.session_state.ohlc_data,
                        initial_capital=100
                    )

                # Check for errors in backtest results
                if "error" in st.session_state.backtest_results:
                    error_msg = st.session_state.backtest_results["error"]
                    st.error(f"Backtest Error: {error_msg}")
                    st.error("Backtesting failed. Please review your strategy or try with a different asset/timeframe.")
                else:
                    # Display results
                    st.subheader("Backtest Results")
                    
                    # Create metrics in a nice dashboard style
                    metric1, metric2, metric3 = st.columns(3)
                    metric1.metric("Initial Capital", f"${st.session_state.backtest_results['initial_capital']:.2f}")
                    metric2.metric("Final Portfolio Value", f"${st.session_state.backtest_results['final_value']:.2f}")
                    metric3.metric("Total Return", f"{st.session_state.backtest_results['return']:.2f}%")
                    
                    # Display enhanced metrics
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Win Rate", f"{st.session_state.backtest_results.get('win_rate', 0):.2f}%")
                        st.metric("Total Trades", st.session_state.backtest_results.get('total_trades', 0))
                    
                    with col2:
                        st.metric("Profitable Trades", st.session_state.backtest_results.get('profitable_trades', 0))
                        st.metric("Losing Trades", st.session_state.backtest_results.get('losing_trades', 0))
                    
                    with col3:
                        st.metric("Max Drawdown", f"{st.session_state.backtest_results.get('max_drawdown', 0):.2f}%")
                        st.metric("Sharpe Ratio", f"{st.session_state.backtest_results.get('sharpe_ratio', 0):.2f}")
                    
                    with col4:
                        st.metric("Avg Profit", f"{st.session_state.backtest_results.get('average_profit', 0):.2f}%")
                        st.metric("Avg Loss", f"{st.session_state.backtest_results.get('average_loss', 0):.2f}%")
                    
                    # Plot equity curve if available
                    equity_curve = st.session_state.backtest_results.get('equity_curve', [])
                    if equity_curve:
                        st.subheader("Equity Curve")
                        # Convert to DataFrame for plotting
                        equity_df = pd.DataFrame(equity_curve)
                        if not equity_df.empty:
                            # Remove timestamp column for plotting
                            equity_df['timestamp'] = pd.to_datetime(equity_df['timestamp'])
                            equity_df.set_index('timestamp', inplace=True)
                            
                            # Create plot with both equity and price
                            chart1, chart2 = st.columns(2)
                            with chart1:
                                st.subheader("Portfolio Value")
                                st.line_chart(equity_df[['equity']])
                            with chart2:
                                st.subheader("Price Chart")
                                st.line_chart(equity_df[['close']])

                    # Show Trade Log
                    st.subheader("Trade Log")
                    trade_log_df = pd.DataFrame(st.session_state.backtest_results['trade_log'])
                    if not trade_log_df.empty:
                        # Add profit column if it exists
                        if 'profit_pct' in trade_log_df.columns:
                            # Format profit_pct for display
                            trade_log_df['profit_pct'] = trade_log_df['profit_pct'].apply(
                                lambda x: f"+{x:.2f}%" if x > 0 else f"{x:.2f}%"
                            )
                            st.dataframe(trade_log_df)
                        else:
                            st.dataframe(trade_log_df)
                        
                        # Add a download button for the trade log
                        csv = trade_log_df.to_csv(index=False).encode('utf-8')
                        st.download_button(
                            label="Download Trade Log as CSV",
                            data=csv,
                            file_name="trade_log.csv",
                            mime="text/csv"
                        )
                    else:
                        st.write("No trades were executed during the backtest period.")

        except ImportError as e:
            st.error(f"Missing dependency: {str(e)}")
            st.info("Try installing the missing package with: pip install -r requirements.txt")
        except Exception as e:
            st.error(f"Error during backtesting: {e}")
            st.error(f"Details: {traceback.format_exc()}")
            st.info("Please try a different strategy or timeframe.")

# Reset Button
col1, col2 = st.columns([1, 5])
with col1:
    if st.button("Reset Session"):
        st.session_state.strategy_params = None
        st.session_state.ohlc_data = None
        st.session_state.strategy_code = None
        st.session_state.backtest_results = None
        st.session_state.data_visualized = False
        st.session_state.code_generated = False
        st.success("Session reset successfully. You can start over.")

# Footer
st.markdown("---")
st.markdown(
    """<div style="text-align: center">
    <p>Crypto Trading Strategy Generator v{} | <a href="https://github.com/user/repo" target="_blank">GitHub</a> | <a href="https://yoursite.com" target="_blank">Documentation</a></p>
    </div>""".format(VERSION),
    unsafe_allow_html=True
)