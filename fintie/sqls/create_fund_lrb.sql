CREATE TABLE IF NOT EXISTS fund_lrb (
    code TEXT,
    pub_date DATE,
    report_period TIMESTAMP,

    -- 营业收入
    revenue                                                     BIGINT,
    revenue_operating                                           BIGINT,

    -- 营业成本
    total_expense                                               BIGINT,
    expense_cost_of_goods_sold                                  BIGINT,
    expense_sales_tax                                           BIGINT,
    expense_selling                                             BIGINT,
    expense_ga                                                  BIGINT,
    expense_prospecting                                         BIGINT,
    expense_financing                                           BIGINT,
    expense_asset_depreciation                                  BIGINT,
    expense_fair_value_change                                   BIGINT,
    expense_investment_income                                   BIGINT,
    expense_investment_income_from_related                      BIGINT,
    expense_exchange_income                                     BIGINT,

    -- 营业利润
    profit_others                                               BIGINT,
    profit_from_operation                                       BIGINT,
    profit_form_operation_subsidy_income                        BIGINT,
    profit_from_operation_non_operating_revenue                 BIGINT,
    profit_from_operation_non_operating_expense                 BIGINT,
    profit_non_current_assets_disposal_loss                     BIGINT,
    profit_before_tax_others                                    BIGINT,
    profit_before_tax                                           BIGINT,
    profit_before_tax_income_tax                                BIGINT,

    -- 净利润
    net_profit_others                                           BIGINT,
    net_profit                                                  BIGINT,
    net_profit_parent_company                                   BIGINT,
    net_profit_minority                                         BIGINT,

    -- 每股收益
    earninggs_per_share                                         BIGINT,
    basic_earnings_per_share                                    BIGINT,
    diluted_earnings_per_share                                  BIGINT,

    other_income                                                BIGINT,

    total_income                                                BIGINT,
    total_income_parent_company                                 BIGINT,
    total_income_minority                                       BIGINT,

    revenue_interest_income                                     BIGINT,
    revenue_premiums_earned                                     BIGINT,
    revenue_commission_income                                   BIGINT,

    expense_interest_expense                                    BIGINT,
    expense_commission_expense                                  BIGINT,
    expense_refunded_premiums                                   BIGINT,
    expense_payoff_cost                                         BIGINT,
    expense_net_provision_insurancecontracts                    BIGINT,
    expense_expenditures_dividend_policy                        BIGINT,
    expense_reinsurance_cost                                    BIGINT,
    profit_non_current_assets_disposal_gains                    BIGINT,
    UNIQUE (code, report_period)
);


/*
利润表（income_statement）

机构ID
机构名称
公告日期
开始日期
截止日期
报告年度
合并类型
报表来源
-- 营业收入
revenue   一、营业总收入
    公司经营所取得的收入总额
    旧准则：营业总收入=主营业务收入 ；
    新准则：(一般企业)营业总收入=营业收入+利息收入+已赚保费+手续费及佣金收入(银行、保险、证券)
revenue_operating   其中：营业收入（元）
    公司经营主要业务所取得的收入总额

-- 营业成本
total_expense   二、营业总成本
    公司经营产生的实际成本
    营业总成本=主营业务成本+其他业务成本+利息支出+手续费及佣金支出+退保金+赔付支出净额+
        提取保险合同准备金净额+保单红利支出+分保费用+营业税金及附加+销售费用+管理费用+
        财务费用+资产减值损失+其他
expense_cost_of_goods_sold   其中：营业成本
    公司经营主要业务产生的实际成本
expense_sales_tax   营业税金及附加
    公司经营主要业务应负担的营业税、消费税、城市维护建设税、资源税、土地增值税和教育费附加等。
expense_selling   销售费用
    销售费用是指企业在销售产品、自制半成品和工业性劳务等过程中发生的各项费用。
expense_ga   管理费用
    管理费用是指企业的行政管理部门为管理和组织经营而发生的各项费用
expense_prospecting   堪探费用
expense_financing   财务费用
    财务费用是指企业为筹集生产经营所需资金等而发生的费用，
    包括利息支出（减利息收入）、汇兑损失（减汇兑收益）以及相关的手续费等。
expense_asset_depreciation   资产减值损失
    资产减值，是指资产的可收回金额低于其账面价值.
expense_fair_value_change     加：公允价值变动净收益
expense_investment_income   投资收益
    投资收益是指企业进行投资所获得的经济利益。
expense_investment_income_from_related     其中：对联营企业和合营企业的投资收益
expense_exchange_income   汇兑收益

-- 营业利润
profit_others  影响营业利润的其他科目
profit_from_operation   三、营业利润
    销售利润是企业在其全部销售业务中实现的利润，又称营业利润、经营利润，它包含主营业务利润。
profit_form_operation_subsidy_income   加：补贴收入
    补贴收入是指国有企业得到的各级财政部门给予的专项补贴收入。
profit_from_operation_non_operating_revenue   营业外收入
    营业外收入是指企业发生的与其生产经营无直接关系的各项收入，
    包括固定资产盘盈、处置固定资产净收益、非货币性交易收益、出售无形资产收益、罚款净收入等。
profit_from_operation_non_operating_expense   减：营业外支出
    营业外支出，是指企业发生的与其生产经营无直接关系的各项支出，
    如固定资产盘亏、处置固定资产净损失、出售无形资产损失、债务重组损失、
    计提的固定资产减值准备、计提的无形资产减值准备、
    计提的在建工程减值准备、罚款支出、捐赠支出、非常损失等。
profit_non_current_assets_disposal_loss     其中：非流动资产处置损失
    非流动资产处置损失包括固定资产处置损失和无形资产出售损失。
profit_before_tax_others    加：影响利润总额的其他科目
profit_before_tax   四、利润总额
    利润总额是指税前利润，也就是企业在所得税前一定时期内经营活动的总成果。
profit_before_tax_income_tax   减：所得税
    所得税是指以纳税人的所得额为课税对象的各种税收的统称。

-- 净利润
net_profit_others   加：影响净利润的其他科目
net_profit   五、净利润
    净利润（收益）是指在利润总额中按规定交纳了所得税以后公司的利润留存，一般也称为税后利润或净收入。
net_profit_parent_company   归属于母公司所有者的净利润
    其反映在企业合并净利润中，归属于母公司股东（所有者）所有的那部分净利润。
net_profit_minority   少数股东损益

-- 每股收益
earninggs_per_share     六、每股收益：
basic_earnings_per_share   （一）基本每股收益
    本每股收益是指企业应当按照属于普通股股东的当期净利润，除以发行在外普通股的加权平均数从而计算出的每股收益。
diluted_earnings_per_share    （二）稀释每股收益
    稀释每股收益是以基本每股收益为基础，假设企业所有发行在外的稀释性潜在普通股均已转换为普通股，
    从而分别调整归属于普通股股东的当期净利润以及发行在外普通股的加权平均数计算而得的每股收益。

other_income   七、其他综合收益
    其他综合收益是指企业根据企业会计准则规定未在损益中确认的各项利得和损失扣除所得税影响后的净额。

total_income   八、综合收益总额
    综合收益总额项目，反映企业净利润与其他综合收益的合计金额。
total_income_parent_company   其中：归属于母公司
total_income_minority   其中：归属于少数股东

revenue_interest_income   利息收入
revenue_premiums_earned   已赚保费
revenue_commission_income   手续费及佣金收入

expense_interest_expense   利息支出
expense_commission_expense   手续费及佣金支出
expense_refunded_premiums   退保金
expense_payoff_cost   赔付支出净额
expense_net_provision_insurancecontracts   提取保险合同准备金净额
expense_expenditures_dividend_policy   保单红利支出
expense_reinsurance_cost   分保费用
profit_non_current_assets_disposal_gains   其中：非流动资产处置利得
 */
