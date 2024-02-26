import { ChangeEvent, useEffect, useState } from "react";
import "./styles/App.scss";
import _ from "lodash";
import axios from "axios";
import { Card, Form, Table } from "react-bootstrap";
import { BarChart } from "@mui/x-charts/BarChart";
import { LineChart } from "@mui/x-charts/LineChart";
import { mangoFusionPalette } from "@mui/x-charts/colorPalettes";
import {
  countries,
  defaultHistogramData,
  months,
  queryNames,
  graphTitles,
} from "./constants";
import { IHistogramData, IHistogramYearlyResponse } from "./types";

function App() {
  const lineStyles = {
    //change left yAxis label styles
    "& .MuiChartsAxis-left .MuiChartsAxis-tickLabel": {
      strokeWidth: 0.6,
      fill: "#fff",
    },
    "& .MuiChartsAxis-left .MuiChartsAxis-label": {
      fill: "#fff",
      marginRight: "30px",
    },
    // change bottom label styles
    "& .MuiChartsAxis-bottom .MuiChartsAxis-tickLabel": {
      strokeWidth: 0.6,
      fill: "#fff",
    },
    // bottomAxis Line Styles
    "& .MuiChartsAxis-bottom .MuiChartsAxis-line": {
      stroke: "#fff",
      strokeWidth: 0.6,
    },
    // leftAxis Line Styles
    "& .MuiChartsAxis-left .MuiChartsAxis-line": {
      stroke: "#fff",
      strokeWidth: 0.6,
    },
    // bottomAxis Tick Styles
    "& .MuiChartsAxis-bottom .MuiChartsAxis-tick": {
      stroke: "#fff",
      strokeWidth: 0.6,
    },
    // leftAxis Tick Styles
    "& .MuiChartsAxis-left .MuiChartsAxis-tick": {
      stroke: "#fff",
      strokeWidth: 0.6,
    },
    // Line chart marker styles
    "& .MuiMarkElement-root": {
      display: "none",
    },
  };

  const barChartSettings = {
    series: [
      { dataKey: "avg_real", label: "Avg Tempetures True" },
      { dataKey: "avg_dp", label: "Avg Tempetures DP" },
      { dataKey: "avg_quantum_dp", label: "Avg Tempetures Quantum DP" },
    ],
    colors: mangoFusionPalette,
    height: 300,
    yAxis: [
      {
        label: "Tempeture",
      },
    ],
    margin: { top: 10, bottom: 30, left: 40, right: 10 },
    slotProps: {
      legend: {
        labelStyle: {
          fontSize: 14,
          fill: "#fff",
        },
      },
    },
    sx: lineStyles,
  };

  const [loading, setLoading] = useState<boolean>(false);
  const [country, setCountry] = useState<string>("japan");
  const [year, setYear] = useState<number>(2010);
  const [dateInterval, setDateInterval] = useState<string>("monthly");
  const [epsilon, setEpsilon] = useState<number>(1);
  const [dataset, setDataset] = useState<IHistogramData[]>([]);
  const [labels, setLabels] = useState<string[]>([]);

  useEffect(() => {
    fetchHistogramData();
  }, [country, year, epsilon, dateInterval]);

  const fetchHistogramData = async () => {
    setLoading(true);
    const requestUrl = `http://127.0.0.1:8000/${
      dateInterval === "yearly" ? "yearly" : ""
    }?country=${country}&year=${year}&budget_percent=${epsilon}`;
    const response = await axios.post(requestUrl);
    if (dateInterval === "yearly") {
      const data: IHistogramYearlyResponse = response.data;
      setDataset(data.data);
      setLabels(data.labels);
    } else {
      const data: IHistogramData[] = response.data;
      setDataset(data);
    }
    setLoading(false);
  };

  const handleCountryChange = (e: ChangeEvent<HTMLSelectElement>) => {
    setCountry(e.target.value);
  };

  const handleYearChange = (e: ChangeEvent<HTMLSelectElement>) => {
    setYear(+e.target.value);
  };

  const handleDateIntervalChange = (e: ChangeEvent<HTMLSelectElement>) => {
    setDateInterval(e.target.value);
    setEpsilon(50);
  };
  const handleEpsilonChange = (e: ChangeEvent<HTMLInputElement>) => {
    _.debounce(() => setEpsilon(+e.target.value));
  };

  const formatPercentage = (percentage: number) => {
    return `${(percentage * 100).toFixed(3)}%`;
  };

  return (
    <div id="app">
      <div className="left-content flex-column">
        <Card className="left-filter">
          <Card.Body>
            <p className="title">Filters</p>
            <Form>
              <Form.Group className="mb-3" controlId="country-select">
                <Form.Label className="s2">Country</Form.Label>
                <Form.Select
                  value={country}
                  onChange={(e) => handleCountryChange(e)}
                >
                  <option>Select country</option>
                  {countries.map((country, i) => (
                    <option value={country} key={i}>
                      {country}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
              <Form.Group className="mb-3" controlId="date-interval-select">
                <Form.Label className="s2">Date Interval</Form.Label>
                <Form.Select
                  value={dateInterval}
                  onChange={(e) => handleDateIntervalChange(e)}
                >
                  <option value="monthly" key="date-interval-option-1">
                    Monthly
                  </option>
                  <option value="yearly" key="date-interval-option-2">
                    Yearly
                  </option>
                </Form.Select>
              </Form.Group>
              {dateInterval === "monthly" && (
                <Form.Group className="mb-3" controlId="year-select">
                  <Form.Label className="s2">Year</Form.Label>
                  <Form.Select
                    value={year}
                    onChange={(e) => handleYearChange(e)}
                  >
                    <option>Select year</option>
                    {_.range(1743, 2014).map((country, i) => (
                      <option value={country} key={i}>
                        {country}
                      </option>
                    ))}
                  </Form.Select>
                </Form.Group>
              )}
              <Form.Group className="mb-3" controlId="epsilon-input">
                <Form.Label className="s2">Epsilon</Form.Label>
                <div className="flex-row ai-c">
                  <Form.Range
                    min={1}
                    max={100}
                    bsPrefix="customized-range-input"
                    value={epsilon}
                    onChange={(e) => handleEpsilonChange(e)}
                  />
                  <p className="s2 epsilon-value">{epsilon}</p>
                </div>
              </Form.Group>
            </Form>
          </Card.Body>
        </Card>
        <p className="title">Average Errors</p>
        <Table striped variant="dark">
          <thead>
            <tr>
              <th></th>
              <th>DP</th>
              <th>Quantum DP</th>
            </tr>
          </thead>
          <tbody>
            {dataset.map((data, i) => (
              <tr key={`query-error-${i}`}>
                <td>{queryNames[i]}</td>
                <td>{formatPercentage(data.errorPercentages.dp_error)}</td>
                <td>
                  {formatPercentage(data.errorPercentages.quantum_dp_error)}
                </td>
              </tr>
            ))}
          </tbody>
        </Table>
      </div>
      <div className="histogram-container flex-column">
        <div className="histogram-grid">
          {loading ? (
            dateInterval === "monthly" ? (
              <BarChart
                dataset={defaultHistogramData}
                xAxis={[
                  {
                    scaleType: "band",
                    data: months,
                  },
                ]}
                {...barChartSettings}
              />
            ) : (
              <LineChart
                dataset={defaultHistogramData}
                xAxis={[
                  {
                    scaleType: "band",
                    data: _.range(2000, 2012),
                  },
                ]}
                {...barChartSettings}
              />
            )
          ) : (
            dataset.map((data, i) => (
              <div className="flex-column ai-fs">
                <p className="title">
                  {dateInterval === "yearly"
                    ? graphTitles[i]
                    : "Monthly Average Temperatures"}
                </p>
                {dateInterval === "monthly" ? (
                  <BarChart
                    key={`graph-${i}`}
                    dataset={data.histogramData}
                    xAxis={[
                      {
                        scaleType: "band",
                        data: months,
                      },
                    ]}
                    {...barChartSettings}
                  />
                ) : (
                  <LineChart
                    key={`graph-${i}`}
                    dataset={data.histogramData.filter(
                      (_, i) => i % 10 === +labels[0] % 10
                    )}
                    xAxis={[
                      {
                        scaleType: "band",
                        data: _.range(
                          +labels[0],
                          +labels[labels.length - 1],
                          10
                        ),
                      },
                    ]}
                    {...barChartSettings}
                  />
                )}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}

export default App;
