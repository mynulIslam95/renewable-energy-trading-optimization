"""Optional Streamlit research dashboard. Run: streamlit run src/renewable_trading/dashboard.py"""
import json
from pathlib import Path


def main():
    import streamlit as st
    st.set_page_config(page_title='Renewable Trading Research', layout='wide')
    st.title('Renewable Energy Trading Research')
    st.caption('Reproducible research dashboard. Demo results use synthetic market observations, not historical trading returns.')
    path = st.text_input('Experiment report path', 'results/demo/report.json')
    report_path = Path(path)
    if not report_path.is_file():
        st.info('Run the research experiment to generate a report, then enter its path.')
        return
    report = json.loads(report_path.read_text())
    st.warning('Data classification: '+report.get('data_classification','unknown'))
    st.subheader('Dataset')
    cols = st.columns(3)
    cols[0].metric('Observations', f"{report['observations']:,}")
    cols[1].metric('Test observations', f"{report['test']:,}")
    cols[2].metric('Meta weight', f"{report['meta_weight_fitted_on_train']:.3f}")
    st.subheader('Forecast evaluation')
    metrics = []
    for strategy, value in report['strategies'].items():
        metrics.append({'Strategy':strategy,'MAE (MW)':value['forecast']['mae_mw'],
                        'RMSE (MW)':value['forecast']['rmse_mw'],
                        'Simulated revenue (EUR)':value['revenue']['simulated_revenue_eur']})
    st.dataframe(metrics, use_container_width=True)
    st.bar_chart({r['Strategy']:r['MAE (MW)'] for r in metrics})
    st.subheader('Battery optimization')
    st.metric('Offline perfect-foresight upper bound',
              f"€{report['battery_24h_offline_upper_bound_eur']:,.2f}")
    schedule_path = report_path.parent/'battery_schedule.csv'
    if schedule_path.exists():
        import csv
        with schedule_path.open(newline='') as f:
            schedule = list(csv.DictReader(f))
        st.line_chart({'Price (EUR/MWh)':[float(r['price_eur_mwh']) for r in schedule],
                       'SOC (MWh)':[float(r['soc_end_mwh']) for r in schedule]})
    st.subheader('Limitations')
    for item in report.get('limitations',[]):
        st.write('• '+item)

if __name__ == '__main__':
    main()
