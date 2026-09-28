import { supabase } from "@/lib/supabase";

type Row = {
  ticker: string;
  current_price: number;
  predicted_price: number;
  predicted_return: number;
  weight: number;
};

async function getLatestRun(): Promise<{ asOfDate: string | null; rows: Row[] }> {
  const { data: latest } = await supabase
    .from("predictions")
    .select("as_of_date")
    .order("as_of_date", { ascending: false })
    .limit(1)
    .maybeSingle();

  if (!latest) return { asOfDate: null, rows: [] };

  const { data: rows } = await supabase
    .from("predictions")
    .select("ticker, current_price, predicted_price, predicted_return, weight")
    .eq("as_of_date", latest.as_of_date)
    .order("weight", { ascending: false });

  return { asOfDate: latest.as_of_date as string, rows: (rows as Row[]) ?? [] };
}

// Re-fetch on every request so the dashboard always shows the latest
// GitHub Actions run without a manual redeploy.
export const revalidate = 0;

export default async function Page() {
  const { asOfDate, rows } = await getLatestRun();

  return (
    <main className="wrap">
      <h1>Portfolio Optimizer</h1>
      <p className="subtitle">
        {asOfDate
          ? `Latest run: ${asOfDate}`
          : "No runs yet - trigger the GitHub Action once to populate Supabase."}
      </p>

      <table>
        <thead>
          <tr>
            <th>Ticker</th>
            <th>Current price</th>
            <th>Predicted price</th>
            <th>Predicted return</th>
            <th>Weight</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.ticker}>
              <td>{row.ticker}</td>
              <td>${row.current_price.toFixed(2)}</td>
              <td>${row.predicted_price.toFixed(2)}</td>
              <td className={row.predicted_return >= 0 ? "pos" : "neg"}>
                {(row.predicted_return * 100).toFixed(2)}%
              </td>
              <td>
                <div className="bar">
                  <div className="fill" style={{ width: `${row.weight * 100}%` }} />
                  <span>{(row.weight * 100).toFixed(1)}%</span>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </main>
  );
}
