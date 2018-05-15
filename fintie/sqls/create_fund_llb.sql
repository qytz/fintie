CREATE TABLE IF NOT EXISTS fund_llb (
    code TEXT,
    pub_date DATE,
    report_period TIMESTAMP,

    -- 经营活动现金流
    opi_cash_from_sales_of_goods_services                       BIGINT,
    opi_refunds_of_taxes                                        BIGINT,
    opi_cash_from_other_operating_activities                    BIGINT,
    opi_cash_from_operating_activities                          BIGINT,
    opo_cash_paid_for_goods_and_services                        BIGINT,
    opo_cash_paid_for_employee                                  BIGINT,
    opo_cash_paid_for_taxes                                     BIGINT,
    opo_cash_paid_for_other_operation_activities                BIGINT,
    opo_cash_paid_for_operation_activities                      BIGINT,
    op_cash_flow_from_operating_activities                      BIGINT,

    -- 投资活动现金流
    ivi_cash_from_disposal_of_investment                        BIGINT,
    ivi_cash_from_gain_of_investment                            BIGINT,
    ivi_cash_from_disposal_of_asset                             BIGINT,
    ivi_cash_from_dispose_subsidiary                            BIGINT,
    ivi_cash_from_other_investment                              BIGINT,
    ivi_cash_received_from_investment                           BIGINT,
    ivo_cash_paid_for_asset                                     BIGINT,
    ivo_cash_paid_for_investment                                BIGINT,
    ivo_cash_paid_for_pledge_loans                              BIGINT,
    ivo_cash_from_subsidiary                                    BIGINT,
    ivo_cash_paid_for_other_investment                          BIGINT,
    ivo_cash_paid_for_investment                                BIGINT,
    iv_cash_flow_from_investment                                BIGINT,

    -- 筹资活动产生的现金流
    fai_cash_from_investors                                     BIGINT,
    fai_cash_from_financial_borrows                             BIGINT,
    fai_cash_from_debt_investors                                BIGINT,
    fai_cash_from_others                                        BIGINT,
    fai_cash_from_financing_activities                          BIGINT,
    fao_cash_paid_for_debt                                      BIGINT,
    fao_cash_paid_for_dividend_and_interest                     BIGINT,
    fao_cash_paid_for_others                                    BIGINT,
    fao_cash_paid                                               BIGINT,
    fa_cash_flow                                                BIGINT,

    cash_from_exchange_rates                                    BIGINT,
    cash_from_other_reasons_                                    BIGINT,

    cash_equivalent_increase                                    BIGINT,
    cash_equivalent_at_beginning                                BIGINT,
    cash_equivalent_at_end                                      BIGINT,

    notes                                                       BIGINT,
    -- 将净利润调节为经营活动现金流量
    net_profit_to_operate_cash_flow                             BIGINT,
    net_profit                                                  BIGINT,
    np_impairment_of_assets                                     BIGINT,
    np_fixed_assets_loss                                        BIGINT,
    np_amortization_of_intangible_assets                        BIGINT,
    np_long_term_expenses                                       BIGINT,
    np_long_term_assets_expneses                                BIGINT,
    np_fixed_assets_discard                                     BIGINT,
    np_fair_value_change_loss                                   BIGINT,
    np_financial_expense                                        BIGINT,
    np_investment_loss                                          BIGINT,
    np_deferred_tax_assets_dec                                  BIGINT,
    np_deferred_tax_loan_inc                                    BIGINT,
    np_stock_goods_dec                                          BIGINT,
    np_operate_receivables_dec                                  BIGINT,
    np_operate_payables_inc                                     BIGINT,
    np_others                                                   BIGINT,
    np_cash_flow_from_operating_activities                      BIGINT,

    -- 2、不涉及现金收支的重大投资和筹资活动：
    non_cash_activities                                         BIGINT,
    nca_debt_to_capital                                         BIGINT,
    nca_convertible_bond_due_one_year                           BIGINT,
    nca_fixed_assets_under_financing_lease                      BIGINT,

    -- 3、现金及现金等价物净变动情况：
    cash_equivalent_changes                                     BIGINT,
    ce_cash_at_end                                              BIGINT,
    ce_cash_at_begining                                         BIGINT,
    ce_cash_equivalent_at_end                                   BIGINT,
    ce_cash_equivalent_at_begining                              BIGINT,
    ce_cash_others                                              BIGINT,
    ce_cash                                                     BIGINT,


    opi_deposit_inc                                             BIGINT,
    opi_borrowing_from_central_bank_inc                         BIGINT,
    opi_orrowing_from_finance_co_inc                            BIGINT,
    opi_cash_form_original_insurance                            BIGINT,
    opi_cash_from_reinsurance                                   BIGINT,
    opi_insurer_deposit_investment                              BIGINT,
    opi_dispose_finacial_assets                                 BIGINT,
    opi_interest_commission                                     BIGINT,
    opi_loan_from_other_banks_inc                               BIGINT,
    opi_buy_back_inc                                            BIGINT,
    opo_cash_for_loan_and_advance_inc                           BIGINT,
    opo_cash_for_deposit_in_cb_and_ib                           BIGINT,
    opo_cash_paid_for_original_insurance                        BIGINT,
    opo_cash_paid_for_interest_commission                       BIGINT,
    opo_cash_paid_for_expenditures_dividend                     BIGINT,

    fai_subsidiary_receive_from_minority                        BIGINT,
    fao_subsidiary_paid_for_minority                            BIGINT,
    ivo_depreciation_investment_real_estate                     BIGINT,
    UNIQUE (code, report_period)
);


/*
现金流量表（cash_flow_statement）

机构ID
机构名称
公告日期
开始日期
截止日期
报告年度
合并类型
报表来源
-- 经营活动现金流
opi_cash_from_sales_of_goods_services   销售商品、提供劳务收到的现金（元 ）
    公司销售商品、提供劳务实际收到的现金
opi_refunds_of_taxes    收到的税费返还
    公司按规定收到的增值税、所得税等税费返还额
opi_cash_from_other_operating_activities    收到其他与经营活动有关的现金
opi_cash_from_operating_activities  经营活动现金流入小计

opo_cash_paid_for_goods_and_services    购买商品、接受劳务支付的现金
    公司购买商品、接受劳务实际支付的现金
opo_cash_paid_for_employee  支付给职工以及为职工支付的现金
    公司实际支付给职工，以及为职工支付的现金，包括本期实际支付给职工的工资、奖金、各种津贴和补贴等
opo_cash_paid_for_taxes     支付的各项税费
    反映企业按规定支付的各种税费，包括本期发生并支付的税费，
    以及本期支付以前各期发生的税费和预交的税金等。
    本项目可以根据"现金"、"银行存款"、"应交税费"等账户的记录分析填列。
opo_cash_paid_for_other_operation_activities    支付其他与经营活动有关的现金
    反映企业支付的其他与经营活动有关的现金支出，
    如罚款支出、支付的差旅费、业务招待费的现金支出、支付的保险费等。
    本项目根据"现金"、"银行存款"、"管理费用""销售费用"、"营业外收入"等有关账户的记录分析填列。
opo_cash_paid_for_operation_activities  经营活动现金流出小计
op_cash_flow_from_operating_activities 经营活动产生的现金流量净额

-- 投资活动现金流
ivi_cash_from_disposal_of_investment   收回投资收到的现金
ivi_cash_from_gain_of_investment  取得投资收益收到的现金
ivi_cash_from_disposal_of_asset    处置固定资产、无形资产和其他长期资产收回的现金净额
ivi_cash_from_dispose_subsidiary  处置子公司及其他营业单位收到的现金净额
ivi_cash_from_other_investment   收到其他与投资活动有关的现金
    公司除了上述各项以外，收到的其他与投资活动有关的现金。
ivi_cash_received_from_investment    投资活动现金流入小计
ivo_cash_paid_for_asset     购建固定资产、无形资产和其他长期资产支付的现金
    公式: 公司购买、建造固定资产，取得无形资产和其他长期资产支付的现金
ivo_cash_paid_for_investment     投资支付的现金
    反映企业进行权益性投资和债权性投资支付的现金，
    包括企业取得的除现金等价物以外的股票投资和债券投资等支付的现金等。
ivo_cash_paid_for_pledge_loans   质押贷款净增加额
ivo_cash_from_subsidiary    取得子公司及其他营业单位支付的现金净额
ivo_cash_paid_for_other_investment   支付其他与投资活动有关的现金
    反映企业除了上述各项以外，支付的其他与投资活动有关的现金流出。
    其他流出如价值较大的，应单列项目反映。本项目可以根据有关账户的记录分析填列。
ivo_cash_paid_for_investment     投资活动现金流出小计
iv_cash_flow_from_investment     投资活动产生的现金流量净额
    指企业长期资产的购建和对外投资活动（不包括现金等价物范围的投资）的现金流入和流出量。
    包括：收回投资、取得投资收益、处置长期资产等活动收到的现金；
    购建固定资产、在建工程、无形资产等长期资产和对外投资等到活动所支付的现金等。

-- 筹资活动产生的现金流
fai_cash_from_investors    吸收投资收到的现金
    反映企业收到的投资者投入现金，包括以发行股票、债券等方式筹集的资金实际收到的净额。
fai_cash_from_financial_borrows    取得借款收到的现金
    公司向银行或其他金融机构等借入的资金。
fai_cash_from_debt_investors FLOAT     发行债券收到的现金
fai_cash_from_others    收到其他与筹资活动有关的现金
    反映企业收到的其他与筹资活动有关的现金流入，如接受现金捐赠等。
fai_cash_from_financing_activities     筹资活动现金流入小计
fao_cash_paid_for_debt  偿还债务支付的现金
    公司以现金偿还债务的本金，包括偿还银行或其他金融机构等的借款本金、偿还债券本金等。
fao_cash_paid_for_dividend_and_interest     分配股利、利润或偿付利息支付的现金
    反映企业实际支付给投资人的利润以及支付的借款利息、债券利息等。
fao_cash_paid_for_others    支付其他与筹资活动有关的现金
    反映企业支付的其他与筹资活动有关的现金流出。如融资租入固定资产支付的租赁费等。
    本项目根据有关账户的记录分析填列。
fao_cash_paid   筹资活动现金流出小计
fa_cash_flow    筹资活动产生的现金流量净额
    指企业接受投资和借入资金导致的现金流入和流出量。
    包括：接受投资、借入款项、发行债券等到活动收到的现金；
    偿还借款、偿还债券、支付利息、分配股利等活动支付的现金等。

cash_from_exchange_rates  四、汇率变动对现金的影响
cash_from_other_reasons_  四(2)、其他原因对现金的影响

cash_equivalent_increase    五、现金及现金等价物净增加额
cash_equivalent_at_beginning   期初现金及现金等价物余额
cash_equivalent_at_end         期末现金及现金等价物余额

notes    附注：
-- 将净利润调节为经营活动现金流量
net_profit_to_operate_cash_flow   1、将净利润调节为经营活动现金流量：
net_profit  净利润
np_impairment_of_assets    加：资产减值准备
np_fixed_assets_loss     固定资产折旧、油气资产折耗、生产性生物资产折旧
np_amortization_of_intangible_assets     无形资产摊销
np_long_term_expenses     长期待摊费用摊销
np_long_term_assets_expneses     处置固定资产、无形资产和其他长期资产的损失
np_fixed_assets_discard     固定资产报废损失
np_fair_value_change_loss     公允价值变动损失
np_financial_expense  财务费用
np_investment_loss     投资损失
np_deferred_tax_assets_dec     递延所得税资产减少
np_deferred_tax_loan_inc        递延所得税负债增加
np_stock_goods_dec     存货的减少
np_operate_receivables_dec     经营性应收项目的减少
np_operate_payables_inc     经营性应付项目的增加
np_others       其他
np_cash_flow_from_operating_activities    经营活动产生的现金流量净额2

-- 2、不涉及现金收支的重大投资和筹资活动：
non_cash_activities        2、不涉及现金收支的重大投资和筹资活动：
nca_debt_to_capital        债务转为资本
nca_convertible_bond_due_one_year        一年内到期的可转换公司债券
nca_fixed_assets_under_financing_lease        融资租入固定资产

-- 3、现金及现金等价物净变动情况：
cash_equivalent_changes 3、现金及现金等价物净变动情况：
ce_cash_at_end     现金的期末余额
ce_cash_at_begining 减：现金的期初余额
ce_cash_equivalent_at_end  加：现金等价物的期末余额
ce_cash_equivalent_at_begining  减：现金等价物的期初余额
ce_cash_others  加：其他原因对现金的影响2
ce_cash 现金及现金等价物净增加额2

opi_deposit_inc    客户存款和同业存放款项净增加额
opi_borrowing_from_central_bank_inc    向中央银行借款净增加额
opi_orrowing_from_finance_co_inc    向其他金融机构拆入资金净增加额
opi_cash_form_original_insurance    收到原保险合同保费取得的现金
opi_cash_from_reinsurance      收到再保险业务现金净额
opi_insurer_deposit_investment    保户储金及投资款净增加额
opi_dispose_finacial_assets    处置以公允价值计量且其变动计入当期损益的金融资产净增加额
opi_interest_commission    收取利息、手续费及佣金的现金
opi_loan_from_other_banks_inc    拆入资金净增加额
opi_buy_back_inc    回购业务资金净增加额
opo_cash_for_loan_and_advance_inc    客户贷款及垫款净增加额
opo_cash_for_deposit_in_cb_and_ib    存放中央银行和同业款项净增加额
opo_cash_paid_for_original_insurance    支付原保险合同赔付款项的现金
opo_cash_paid_for_interest_commission    支付利息、手续费及佣金的现金
opo_cash_paid_for_expenditures_dividend    支付保单红利的现金

fai_subsidiary_receive_from_minority    其中：子公司吸收少数股东投资收到的现金
fao_subsidiary_paid_for_minority    其中：子公司支付给少数股东的股利、利润
ivo_depreciation_investment_real_estate    投资性房地产的折旧及摊销
*/
