from flask import Flask, request, jsonify
from tax_calculator import calculate_tax

app = Flask(__name__)


@app.route("/api/tax/calculate", methods=["POST"])
def calculate():
    try:
        data = request.get_json()

        required_fields = [
            "monthly_income",
            "cumulative_income",
            "cumulative_tax_free_deduction",
            "cumulative_special_deduction",
            "months_count",
        ]
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"缺少必填字段: {field}"}), 400

        result = calculate_tax(
            monthly_income=float(data["monthly_income"]),
            cumulative_income=float(data["cumulative_income"]),
            cumulative_tax_free_deduction=float(data["cumulative_tax_free_deduction"]),
            cumulative_special_deduction=float(data["cumulative_special_deduction"]),
            months_count=int(data["months_count"]),
            cumulative_prepaid_tax=float(data.get("cumulative_prepaid_tax", 0.0)),
            cumulative_special_additional_deduction=float(
                data.get("cumulative_special_additional_deduction", 0.0)
            ),
            cumulative_other_deduction=float(data.get("cumulative_other_deduction", 0.0)),
        )

        return jsonify(
            {
                "code": 0,
                "message": "success",
                "data": result,
            }
        )
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception as e:
        return jsonify({"error": f"服务器内部错误: {str(e)}"}), 500


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
